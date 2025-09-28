
import mysql from "mysql2/promise";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import dotenv from "dotenv";

import express from "express";
import multer from "multer";
import fetch from "node-fetch";
import fs from "fs";
import FormData from "form-data";

dotenv.config();




const app = express();
const upload = multer({ dest: "uploads/" });
app.use(express.json());

const db = await mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
});

// ---------------- Helpers ----------------
function authMiddleware(req, res, next) {

  const token = req.headers["authorization"]?.split(" ")[1];
  if (!token) return res.status(401).json({ error: "Unauthorized" });

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        //console.log("Decoded JWT:", decoded);  // should now show { id: 1, username: 'akash' }
        req.user = decoded;
        next();
    } catch (err) {
        console.error("JWT verify error:", err);
        return res.status(401).json({ error: "Invalid token" });
    }
}

// ---------------- Auth APIs ----------------

// Signup
app.post("/signup", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "Email and password are required" });
  }
  const hash = await bcrypt.hash(password, 10);

  try {
    const [result] = await db.query(
      "INSERT INTO users (username, password_hash) VALUES (?, ?)",
      [username, hash]
    );
    res.json({ id: result.insertId, username });
  } catch (err) {
  console.error("Signup error:", err);
  res.status(400).json({ error: err.message });
}
});

// Login
// Login
app.post("/login", async (req, res) => {
  const { username, password } = req.body;

  const [rows] = await db.query("SELECT * FROM users WHERE username = ?", [username]);
  if (rows.length === 0) return res.status(400).json({ error: "Invalid credentials" });

  const user = rows[0];
  const match = await bcrypt.compare(password, user.password_hash);

  if (!match) return res.status(400).json({ error: "Invalid credentials" });

  // Sign JWT with user info in payload
  const token = jwt.sign(
    { id: user.id, username: user.username },  // <-- payload now has user info
    process.env.JWT_SECRET,
    { expiresIn: "1h" }
  );

  res.json({ token });
});


// ---------------- Proxy: process_image_stepwise ----------------
app.post("/process_image_stepwise", authMiddleware, upload.single("file"), async (req, res) => {
  try {
    const formData = new FormData();
    formData.append("file", fs.createReadStream(req.file.path));

    const response = await fetch("http://127.0.0.1:8000/process_image_stepwise", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    // Save result in DB
    await db.query("INSERT INTO results (user_id, pipeline) VALUES (?, ?)", [
      req.user.id,
      JSON.stringify(data.pipeline),
    ]);

    res.json(data);
  } catch (err) {
    console.error("Error forwarding to FastAPI:", err);
    res.status(500).json({ error: "Failed to process stepwise" });
  }
});

// ---------------- Fetch User Results ----------------
app.get("/results", authMiddleware, async (req, res) => {
  const [rows] = await db.query(
    "SELECT id, pipeline, created_at FROM results WHERE user_id = ? ORDER BY created_at DESC",
    [req.user.id]
  );
  res.json(rows);
});

// ---------------- Start Node server ----------------
app.listen(8001, () => {
  console.log("Node proxy server running at http://127.0.0.1:8001");
});
