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

const publish = (topic, payload, options = {}) => {
    if (client.connected) {
        const message = JSON.stringify(payload);
        client.publish(topic, message, options, (err) => {
            if (err) {
                console.error(`Falha ao publicar MQTT no tópico ${topic}:`, err);
            }
        });
    } else {
        console.error(`Cliente MQTT não conectado. Mensagem para o tópico ${topic} não foi enviada.`);
    }
};

module.exports = { publish };