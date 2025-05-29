const express = require('express');
const config = require('./src/config');
const connectDB = require('./src/config/db');
const mainApiRouter = require('./src/routes/index.routes');

const app = express();

connectDB();

app.use(express.json());
app.use('/api', mainApiRouter); 
app.use((req, res, next) => {
  res.status(404).json({ message: 'Sorry, can\'t find that!' });
});
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Something broke!', error: err.message });
});


const PORT = config.port || 3000;
app.listen(PORT, () => {
  console.log(`Servidor do estacionamento aberto em http://localhost:${PORT}`);
});