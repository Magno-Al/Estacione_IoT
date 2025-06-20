const express = require('express');
const router = express.Router();
const serviceController = require('../controllers/service.controller');

router.post('/entry', serviceController.recordEntry);
router.put('/exit/:license_plate', serviceController.recordExit);
router.get('/', serviceController.getAllServiceRecords);
router.get('/calculate-fee/:license_plate', serviceController.calculateCurrentFee);
router.get('/entry-time/:license_plate', serviceController.getEntryTimeByLicensePlate);
router.get('/plate/:license_plate', serviceController.getServiceRecordByLicensePlate);
router.get('/:customer_id', serviceController.getServiceRecordsByCustomerId);
router.get('/active-count', serviceController.getActiveVehicleCount);
router.get('/profit/by-date/:date', serviceController.getProfitByDate);
router.get('/entries/by-date/:date', serviceController.getEntryCountByDate);
router.put('/confirm-payment/:id', serviceController.confirmPayment);

module.exports = router;