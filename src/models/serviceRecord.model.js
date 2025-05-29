const mongoose = require('mongoose');

const serviceRecordSchema = new mongoose.Schema({
  license_plate: { type: String, required: true, uppercase: true, trim: true },
  customer_id: { type: mongoose.Schema.Types.ObjectId, ref: 'CustomerRegistry' },
  customer_name: { type: String },
  in_service: { type: Boolean, default: true },
  entry_timestamp: { type: Date, default: Date.now },
  exit_timestamp: { type: Date, default: null },
  fee_amount: { type: Number, default: 0 },
  amount_paid: { type: Number, default: 0 },
  is_paid: { type: Boolean, default: false }
});

const ServiceRecord = mongoose.model('ServiceRecord', serviceRecordSchema, 'service_records');

module.exports = ServiceRecord;