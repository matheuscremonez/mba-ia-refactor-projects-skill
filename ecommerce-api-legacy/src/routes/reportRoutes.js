const express = require('express');
const router = express.Router();
const reportController = require('../controllers/reportController');

router.get('/financial-report', async (req, res) => {
  try {
    const report = await reportController.getFinancialReport();
    return res.json(report);
  } catch (err) {
    return res.status(500).json({ error: 'Erro interno do servidor' });
  }
});

module.exports = router;
