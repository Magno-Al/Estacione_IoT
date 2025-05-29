const mongoose = require('mongoose');

const customerRegistrySchema = new mongoose.Schema({
  vehicles: [{ type: String, uppercase: true, trim: true }],
  customer_name: { type: String, required: true },
  customer_email: { type: String, required: true, unique: true, lowercase: true, trim: true },
  active: { type: Boolean, default: true },
  created_at: { type: Date, default: Date.now }
});

const CustomerRegistry = mongoose.model('CustomerRegistry', customerRegistrySchema, 'customer_registry');

module.exports = CustomerRegistry;