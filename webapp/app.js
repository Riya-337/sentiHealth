const express = require('express');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { faker } = require('@faker-js/faker');

const app = express();
app.use(express.json());

const dbDir = '../data';
if (!fs.existsSync(dbDir)) fs.mkdirSync(dbDir);
fs.writeFileSync('../data/app.db', 'MOCK DB FOR DEMO');

const patients = [];
for (let i = 0; i < 1000; i++) {
  patients.push({ id: uuidv4(), name: faker.person.fullName(), dob: faker.date.past().toISOString() });
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
  res.json(patients.slice(0, limit));
});
app.get('/appointments', (req, res) => res.json([]));
app.get('/records/:id', (req, res) => res.json({ id: req.params.id }));
app.get('/health', (req, res) => res.status(200).send('OK'));

app.listen(3000, () => console.log('Server running on port 3000'));
