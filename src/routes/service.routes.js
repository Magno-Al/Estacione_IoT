const express = require('express');
const router = express.Router();
const serviceController = require('../controllers/service.controller');

router.post('/entry', serviceController.recordEntry);
router.put('/exit/:license_plate', serviceController.recordExit);
router.get('/', serviceController.getAllServiceRecords);
router.get('/calculate-fee/:license_plate', serviceController.calculateCurrentFee);

module.exports = router;