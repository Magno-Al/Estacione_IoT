const CustomerRegistry = require('../models/customerRegistry.model');
const mqttService = require('../services/mqttService'); 

exports.createCustomer = async (req, res) => {
  try {
    const {id, vehicles, customer_name, customer_email } = req.body;

    if (!id || !vehicles || !customer_name || !customer_email) {
      return res.status(400).json({ message: 'Vehicles, customer_name, and customer_email are required fields.' });
    }

    const newCustomerData = {
      _id: id,
      vehicles,
      customer_name,
      customer_email
      // active: true
    };

    const newCustomer = new CustomerRegistry(newCustomerData);
    await newCustomer.save();
    if (newCustomer) {
      await publishCustomerStats();
      res.status(201).json(newCustomer);
    }
  } 
  catch (error) {
    if (error.code === 11000 && error.keyPattern && error.keyPattern.customer_email) {
      return res.status(409).json({ message: 'Error creating customer: Email already exists.', error: error.message });
    }
    res.status(400).json({ message: 'Error creating customer', error: error.message });
  }
};

exports.getAllCustomers = async (req, res) => {
  try {
    const customers = await CustomerRegistry.find();
    res.status(200).json(customers);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching customers', error: error.message });
  }
};

exports.getCustomerById = async (req, res) => {
  try {
    const customer = await CustomerRegistry.findById(req.params.id);
    if (!customer) {
      return res.status(404).json({ message: 'Customer not found' });
    }
    res.status(200).json(customer);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching customer', error: error.message });
  }
};

exports.getCustomerIdByEmail = async (req, res) => {
  try {
    const customer = await CustomerRegistry.findOne({ customer_email: req.params.email });
    if (!customer) {
      return res.status(404).json({ message: 'Customer not found' });
    }
    res.status(200).json({ customer_id: customer._id });
  }
  catch (error) {
    res.status(500).json({ message: 'Error fetching customer by email', error: error.message });
  }
};

exports.addVehicleToCustomer = async (req, res) => {
  try {
    const { customer_id, license_plate } = req.body;

    if (!customer_id || !license_plate) {
      return res.status(400).json({ message: 'Customer ID and license plate are required.' });
    }

    const normalizedPlate = license_plate.toUpperCase().trim();
    const customer = await CustomerRegistry.findById(customer_id);

    if (!customer) {
      return res.status(404).json({ message: 'Customer not found' });
    }

    if (customer.vehicles.includes(normalizedPlate)) {
      return res.status(400).json({ message: 'Vehicle already exists for this customer.' });
    }

    customer.vehicles.push(normalizedPlate);
    await customer.save();
    res.status(200).json(customer);
  } catch (error) {
    res.status(500).json({ message: 'Error adding vehicle to customer', error: error.message });
  }
}

exports.removeVehicleFromCustomer = async (req, res) => {
  try {
    const { customer_id, license_plate } = req.body;

    if (!customer_id || !license_plate) {
      return res.status(400).json({ message: 'Customer ID and license plate are required.' });
    }

    const normalizedPlate = license_plate.toUpperCase().trim();
    const customer = await CustomerRegistry.findById(customer_id);

    if (!customer) {
      return res.status(404).json({ message: 'Customer not found' });
    }

    if (!customer.vehicles.includes(normalizedPlate)) {
      return res.status(404).json({ message: 'Vehicle not found for this customer.' });
    }

    customer.vehicles = customer.vehicles.filter(vehicle => vehicle !== normalizedPlate);
    await customer.save();
    res.status(200).json(customer);

  } catch (error) {
    res.status(500).json({ message: 'Error removing vehicle from customer', error: error.message });
  }
}

exports.getCustomerByPlate = async (req, res) => {
  try {
    const { plate } = req.params;

    const customer = await CustomerRegistry.findOne({ vehicles: plate.toUpperCase() });

    if (!customer) {
      return res.status(404).json({ message: 'Customer not found for this plate.' });
    }
    res.status(200).json(customer);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching customer by plate', error: error.message });
  }
};

exports.updateCustomer = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body; 

    const updatedCustomer = await CustomerRegistry.findByIdAndUpdate(
      id, 
      updateData, 
      { new: true, runValidators: true }
    );

    if (!updatedCustomer) {
      return res.status(404).json({ message: 'Customer not found.' });
    }

    await publishCustomerStats();

    res.status(200).json({ message: 'Customer updated successfully', customer: updatedCustomer });

  } catch (error) {
    res.status(400).json({ message: 'Error updating customer', error: error.message });
  }
};
// exports.deleteCustomer = async (req, res) => { ... };

//==========================================================================================================
async function publishCustomerStats() {
    const active_count = await CustomerRegistry.countDocuments({ active: true });
    const inactive_count = await CustomerRegistry.countDocuments({ active: false });
    mqttService.publish('parking/status/customer_stats', { active: active_count, inactive: inactive_count }, { retain: true });
}