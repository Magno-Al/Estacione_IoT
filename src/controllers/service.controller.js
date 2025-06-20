const ServiceRecord = require('../models/serviceRecord.model');
const CustomerRegistry = require('../models/customerRegistry.model');

exports.recordEntry = async (req, res) => {
  try {
    const { license_plate } = req.body;

    if (!license_plate) {
      return res.status(400).json({ message: 'License plate is required' });
    }

    const existingActiveService = await ServiceRecord.findOne({ license_plate: license_plate.toUpperCase().trim(), in_service: true });
    if (existingActiveService) {
      return res.status(409).json({ message: 'Vehicle already has an active service record', record: existingActiveService });
    }
    
    let customerNameForRecord = null;
    let customerIdForRecord = null;
    const customer = await CustomerRegistry.findOne({ vehicles: license_plate.toUpperCase().trim(), active: true });
    if (customer) {
      customerNameForRecord = customer.customer_name;
      customerIdForRecord = customer._id;
    }

    const newServiceRecordData = {
      license_plate: license_plate.toUpperCase().trim(),
      customer_name: customerNameForRecord,
      customer_id: customerIdForRecord,
      entry_timestamp: new Date(),
      in_service: true
    };

    const newServiceRecord = new ServiceRecord(newServiceRecordData);
    await newServiceRecord.save();
    res.status(201).json(newServiceRecord);
  } catch (error) {
    res.status(400).json({ message: 'Error recording vehicle entry', error: error.message });
  }
};

exports.recordExit = async (req, res) => {
  try {
    const { license_plate } = req.params;
    const { amount_paid, fee_amount } = req.body;

    const serviceRecord = await ServiceRecord.findOneAndUpdate(
      { license_plate: license_plate, in_service: true },
      { 
        $set: { 
          in_service: false, 
          exit_timestamp: new Date(),
          fee_amount: fee_amount || 0,
          amount_paid: amount_paid || 0,
          is_paid: (amount_paid || 0) >= (fee_amount || 0)
        } 
      },
      { new: true }
    );

    if (!serviceRecord) {
      return res.status(404).json({ message: 'Active service record not found for this license plate or already exited.' });
    }
    res.status(200).json({ message: 'Vehicle exit recorded successfully', record: serviceRecord });
  } catch (error) {
    res.status(400).json({ message: 'Error recording vehicle exit', error: error.message });
  }
};

exports.getAllServiceRecords = async (req, res) => {
  try {
    const records = await ServiceRecord.find().sort({ entry_timestamp: -1 });
    res.status(200).json(records);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching service records', error: error.message });
  }
};

exports.calculateCurrentFee = async (req, res) => {
  try {
    const { license_plate } = req.params;

    if (!license_plate) {
      return res.status(400).json({ message: 'License plate is required in URL parameters.' });
    }

    const serviceRecord = await ServiceRecord.findOne({
      license_plate: license_plate.toUpperCase().trim(),
      in_service: true,
    });

    if (!serviceRecord) {
      return res.status(404).json({ message: 'No active service record found for this license plate.' });
    }

    const entryTime = new Date(serviceRecord.entry_timestamp);
    const currentTime = new Date();

    const durationMilliseconds = currentTime.getTime() - entryTime.getTime();

    const durationMinutes = durationMilliseconds > 0 ? Math.ceil(durationMilliseconds / (1000 * 60)) : 0;
    const feePerMinute = 0.50;
    const calculatedFee = durationMinutes * feePerMinute;

    serviceRecord.fee_amount = calculatedFee;
    await serviceRecord.save();

    res.status(200).json({
      message: 'Valor calculado com sucesso!',
      license_plate: serviceRecord.license_plate,
      entry_timestamp: serviceRecord.entry_timestamp,
      calculation_timestamp: currentTime,
      duration_in_minutes: durationMinutes,
      calculated_fee: calculatedFee,
      service_record_id: serviceRecord._id,
      updated_record: serviceRecord
    });

  } catch (error) {
    console.error("Error in calculateCurrentFee:", error);
    res.status(500).json({ message: 'Error calculating fee for service', error: error.message });
  }
};

exports.getActiveVehicleCount = async (req, res) => {
  try {
    const count = await ServiceRecord.countDocuments({ in_service: true });

    res.status(200).json({
      message: 'Contagem de veículos feita com sucesso.',
      active_vehicles: count
    });
  } catch (error) {
    console.error("Error in getActiveVehicleCount:", error); // Log do erro no servidor
    res.status(500).json({ message: 'Error retrieving active vehicle count', error: error.message });
  }
};

exports.getProfitByDate = async (req, res) => {
  try {
    const dateStr = req.params.date;

    if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return res.status(400).json({ message: 'Formato de data invalido. Use YYYY-MM-DD.' });
    }

    const startDate = new Date(`${dateStr}T00:00:00.000Z`);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 1);

    const result = await ServiceRecord.aggregate([
      {
        $match: {
          in_service: false,
          exit_timestamp: {
            $gte: startDate,
            $lt: endDate
          }
        }
      },
      {
        $group: {
          _id: null,
          total_profit: { $sum: "$amount_paid" }
        }
      }
    ]);

    const profit = result.length > 0 ? result[0].total_profit : 0;

    res.status(200).json({
      date: dateStr,
      total_profit: profit
    });

  } catch (error) {
    console.error("Error in getProfitByDate:", error);
    res.status(500).json({ message: 'Error retrieving profit data', error: error.message });
  }
};

exports.getEntryCountByDate = async (req, res) => {
  try {
    const dateStr = req.params.date;

    if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return res.status(400).json({ message: 'Invalid date format. Please use YYYY-MM-DD.' });
    }

    const startDate = new Date(`${dateStr}T00:00:00.000Z`);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 1);

    const count = await ServiceRecord.countDocuments({
      entry_timestamp: {
        $gte: startDate,
        $lt: endDate
      }
    });

    res.status(200).json({
      date: dateStr,
      entry_count: count
    });

  } catch (error) {
    console.error("Error in getEntryCountByDate:", error);
    res.status(500).json({ message: 'Error retrieving entry count data', error: error.message });
  }
};

exports.confirmPayment = async (req, res) => {
  try {
    const { id } = req.params;

    const serviceRecord = await ServiceRecord.findById(id);

    if (!serviceRecord) {
      return res.status(404).json({ message: 'Service record not found.' });
    }
    
    serviceRecord.amount_paid = serviceRecord.fee_amount;
    serviceRecord.is_paid = true;

    await serviceRecord.save();

    res.status(200).json({
      message: 'Payment confirmed successfully.',
      updated_record: serviceRecord
    });

  } catch (error) {
    console.error("Error in confirmPayment:", error);
    res.status(500).json({ message: 'Error confirming payment', error: error.message });
  }
};