const express = require('express');
const router = express.Router();

const customerRoutes = require('./customer.routes');
const serviceRoutes = require('./service.routes');

router.get('/', (req, res) => {
  res.send('Api do estacionamento rodando!');
});

router.use('/customers', customerRoutes);
router.use('/services', serviceRoutes);

module.exports = router;