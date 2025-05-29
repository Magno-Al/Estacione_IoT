const mongoose = require('mongoose');
const config = require('./index');

const connectDB = async () => {
  try {
    await mongoose.connect(config.mongodbUri);
    console.log(`Sucesso ao conecter com MongoDB em ${config.mongodbUri}`);
  } catch (err) {
    console.error('Falha ao conectar com MongoDB', err);
    process.exit(1);
  }
};

module.exports = connectDB;