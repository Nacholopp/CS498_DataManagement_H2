const express = require("express");
const { Datastore } = require("@google-cloud/datastore");

const app = express();
app.use(express.json());

const datastore = new Datastore();
const KIND = "User";

app.get("/greeting", (req, res) => {
  res.status(200).send("<h1>Hello World!</h1>");
});

app.post("/register", async (req, res) => {
  try {
    const username = (req.body?.username || "").toString().trim();
    if (!username) return res.status(400).json({ error: "username required" });

    const key = datastore.key([KIND, username]);
    await datastore.save({
      key,
      data: { username, createdAt: new Date().toISOString() },
    });

    res.status(200).json({ message: "User registered" });
  } catch (e) {
    console.error("REGISTER ERROR:", e);
    res.status(500).json({ error: "internal error" });
  }
});

app.get("/list", async (req, res) => {
  try {
    const query = datastore.createQuery(KIND);
    const [users] = await datastore.runQuery(query);
    res.status(200).json({ users: users.map(u => u.username).filter(Boolean) });
  } catch (e) {
    console.error("LIST ERROR:", e);
    res.status(500).json({ error: "internal error" });
  }
});

app.post("/clear", async (req, res) => {
  try {
    const query = datastore.createQuery(KIND).select("__key__");
    const [entities] = await datastore.runQuery(query);
    const keys = entities.map(e => e[datastore.KEY]);

    const BATCH = 500;
    for (let i = 0; i < keys.length; i += BATCH) {
      await datastore.delete(keys.slice(i, i + BATCH));
    }

    res.status(200).json({ message: "Cleared" });
  } catch (e) {
    console.error("CLEAR ERROR:", e);
    res.status(500).json({ error: "internal error" });
  }
});

app.listen(8080, "0.0.0.0", () => {
  console.log("Server running on port 8080");
});
