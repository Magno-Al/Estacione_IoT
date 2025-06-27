const dotenv = require('dotenv');

dotenv.config();

module.exports = {
  port: process.env.PORT,
  mongodbUri: process.env.MONGODB_URI,
  mqtt: {
    host: process.env.MQTT_HOST,
    port: process.env.MQTT_PORT || 1883 // Usa a porta 1883 como padrão
  }
};