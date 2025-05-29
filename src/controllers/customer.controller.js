const CustomerRegistry = require('../models/customerRegistry.model');

exports.createCustomer = async (req, res) => {
  try {
    const { vehicles, customer_name, customer_email } = req.body;

    if (!vehicles || !customer_name || !customer_email) {
      return res.status(400).json({ message: 'Vehicles, customer_name, and customer_email are required fields.' });
    }

    const newCustomerData = {
      vehicles,
      customer_name,
      customer_email
      // active: true
    };

    const newCustomer = new CustomerRegistry(newCustomerData);
    await newCustomer.save();
    res.status(201).json(newCustomer);
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

// exports.updateCustomer = async (req, res) => { ... };
// exports.deleteCustomer = async (req, res) => { ... };