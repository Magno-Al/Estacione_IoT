const express = require('express');
const router = express.Router();
const customerController = require('../controllers/customer.controller');

router.post('/', customerController.createCustomer);
router.get('/', customerController.getAllCustomers);
router.get('/:id', customerController.getCustomerById);
router.get('/email/:email', customerController.getCustomerIdByEmail);
// router.put('/:id', customerController.updateCustomer);
// router.delete('/:id', customerController.deleteCustomer);
router.put('/vehicle', customerController.addVehicleToCustomer);
router.delete('/vehicle', customerController.removeVehicleFromCustomer);

module.exports = router;