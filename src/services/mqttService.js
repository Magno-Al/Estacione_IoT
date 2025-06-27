const mqtt = require('mqtt');
const config = require('../config');

const brokerUrl = `mqtt://${config.mqtt.host}:${config.mqtt.port}`;

const client = mqtt.connect(brokerUrl);

client.on('connect', () => {
    console.log(`API conectada ao MQTT Broker em ${brokerUrl}`);
});

client.on('error', (err) => {
    console.error('Erro na conexão MQTT da API:', err);
});

const publish = (topic, message, options) => {
    if (client.connected) {
        client.publish(topic, message, options, (err) => {
            if (err) {
                console.error('Falha ao publicar mensagem MQTT:', err);
            }
        });
    } else {
        console.error('Cliente MQTT não conectado. Mensagem não publicada.');
    }
};

module.exports = { publish };