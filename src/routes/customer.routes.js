const express = require('express');
const router = express.Router();
const customerController = require('../controllers/customer.controller');

router.post('/', customerController.createCustomer);
router.get('/', customerController.getAllCustomers);
router.get('/:id', customerController.getCustomerById);
router.get('/email/:email', customerController.getCustomerIdByEmail);
router.get('/by-plate/:plate', customerController.getCustomerByPlate);
router.put('/vehicle', customerController.addVehicleToCustomer);
router.put('/:id', customerController.updateCustomer);
router.delete('/vehicle', customerController.removeVehicleFromCustomer);

// router.put('/:id', customerController.updateCustomer);
// router.delete('/:id', customerController.deleteCustomer);


module.exports = router;