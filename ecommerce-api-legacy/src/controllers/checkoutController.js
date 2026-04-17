const bcrypt = require('bcrypt');
const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');

const CARD_APPROVED_PREFIX = '4';

async function checkout(data) {
  const { usr: name, eml: email, pwd: password, c_id: courseId, card } = data;

  if (!name || !email || !courseId || !card) {
    return { error: 'Campos obrigatórios ausentes: usr, eml, c_id, card', status: 400 };
  }

  const course = await courseModel.findActiveById(courseId);
  if (!course) {
    return { error: 'Curso não encontrado', status: 404 };
  }

  const paymentStatus = card.startsWith(CARD_APPROVED_PREFIX) ? 'PAID' : 'DENIED';
  if (paymentStatus === 'DENIED') {
    return { error: 'Pagamento recusado', status: 400 };
  }

  let user = await userModel.findByEmail(email);
  if (!user) {
    const passwordHash = await bcrypt.hash(password || '123456', 10);
    const newUserId = await userModel.create(name, email, passwordHash);
    user = { id: newUserId };
  }

  const enrollmentId = await enrollmentModel.create(user.id, courseId);
  await enrollmentModel.createPayment(enrollmentId, course.price, paymentStatus);
  await enrollmentModel.createAuditLog(`Checkout curso ${courseId} por ${user.id}`);

  return { data: { msg: 'Sucesso', enrollment_id: enrollmentId }, status: 200 };
}

module.exports = { checkout };
