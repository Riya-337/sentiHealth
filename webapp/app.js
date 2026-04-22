const express = require('express');
const fs = require('fs');
const Database = require('better-sqlite3');
const { v4: uuidv4 } = require('uuid');
const { faker } = require('@faker-js/faker');

const app = express();
app.use(express.json());

const dbDir = '../data';
if (!fs.existsSync(dbDir)) fs.mkdirSync(dbDir);
const db = new Database('../data/app.db');

db.exec(`
  CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT,
    dob TEXT
  )
`);

const stmt = db.prepare('SELECT COUNT(*) as c FROM patients');
if (stmt.get().c === 0) {
  const insert = db.prepare('INSERT INTO patients (id, name, dob) VALUES (?, ?, ?)');
  for (let i = 0; i < 1000; i++) {
    insert.run(uuidv4(), faker.person.fullName(), faker.date.past().toISOString());
  }
}

app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const log = {
      timestamp: new Date().toISOString(),
      endpoint: req.path,
      method: req.method,
      user_id: req.headers['user-id'] || 'anonymous',
      ip_address: req.ip,
      response_time_ms: Date.now() - start,
      status_code: res.statusCode,
      session_id: req.headers['session-id'] || uuidv4()
    };
    fs.appendFileSync('../logs/events.jsonl', JSON.stringify(log) + '\n');
  });
  next();
});

app.post('/login', (req, res) => res.status(200).send({ token: 'test-token' }));
app.get('/patients', (req, res) => {
  const limit = req.query.limit || 10;
  const patients = db.prepare('SELECT * FROM patients LIMIT ?').all(limit);
  res.json(patients);
});
app.get('/appointments', (req, res) => res.json([]));
app.get('/records/:id', (req, res) => res.json({ id: req.params.id }));
app.get('/health', (req, res) => res.status(200).send('OK'));

app.listen(3000, () => console.log('Server running on port 3000'));
