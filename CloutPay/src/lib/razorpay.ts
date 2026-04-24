import { PUBLIC_RAZORPAY_KEY } from '$env/static/public';
import { createOrder, verifyPayment } from './api';

function loadRazorpayScript(): Promise<void> {
	return new Promise((resolve, reject) => {
		if (document.getElementById('razorpay-sdk')) return resolve();
		const script = document.createElement('script');
		script.id = 'razorpay-sdk';
		script.src = 'https://checkout.razorpay.com/v1/checkout.js';
		script.onload = () => resolve();
		script.onerror = () => reject(new Error('Failed to load Razorpay SDK'));
		document.body.appendChild(script);
	});
}

export async function initiatePayment(amount: number, userName: string, token?: string | null, anonymous = false) {
	await loadRazorpayScript();

	const order = await createOrder(amount, token);

	return new Promise((resolve, reject) => {
		const rzp = new (window as any).Razorpay({
			key: PUBLIC_RAZORPAY_KEY,
			amount: order.amount,
			currency: order.currency ?? 'INR',
			order_id: order.order_id,
			name: 'CloutPay',
			description: 'Support & Climb the Leaderboard',
			modal: {
				ondismiss: () => reject(new Error('cancelled'))
			},
			handler: async (response: Record<string, string>) => {
				try {
					const result = await verifyPayment(
						{
							razorpay_order_id: order.order_id,
							razorpay_payment_id: response.razorpay_payment_id,
							razorpay_signature: response.razorpay_signature,
							user_name: userName,
							anonymous: String(anonymous)
						},
						token
					);
					resolve(result);
				} catch (e) {
					reject(e);
				}
			},
			prefill: { name: anonymous ? '' : userName },
			theme: { color: '#ff4d4d' }
		});
		rzp.on('payment.failed', (res: any) => reject(new Error(res.error.description)));
		rzp.open();
	});
}
