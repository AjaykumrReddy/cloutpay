import { PUBLIC_CASHFREE_ENV } from '$env/static/public';
import { createOrder, verifyPayment } from './api';

function loadCashfreeSDK(): Promise<void> {
	return new Promise((resolve, reject) => {
		if (document.getElementById('cashfree-sdk')) return resolve();
		const script = document.createElement('script');
		script.id = 'cashfree-sdk';
		script.src = 'https://sdk.cashfree.com/js/v3/cashfree.js';
		script.onload = () => resolve();
		script.onerror = () => reject(new Error('Failed to load Cashfree SDK'));
		document.body.appendChild(script);
	});
}

export async function initiatePayment(
	amount: number,
	userName: string,
	token?: string | null,
	anonymous = false
) {
	await loadCashfreeSDK();

	const order = await createOrder(amount, token);

	const mode = PUBLIC_CASHFREE_ENV === 'PRODUCTION' ? 'production' : 'sandbox';

	return new Promise((resolve, reject) => {
		const cashfree = new (window as any).Cashfree({ mode });

		cashfree.checkout({
			paymentSessionId: order.payment_session_id,
			redirectTarget: '_modal',
		}).then(async (result: any) => {
			if (result.error) {
				if (result.error.message?.toLowerCase().includes('cancel')) {
					return reject(new Error('cancelled'));
				}
				return reject(new Error(result.error.message || 'Payment failed'));
			}

			if (result.paymentDetails) {
				try {
					const verification = await verifyPayment(
						{
							cf_order_id: order.cf_order_id,
							user_name: anonymous ? '' : userName,
							anonymous: String(anonymous),
						},
						token
					);
					resolve(verification);
				} catch (e) {
					reject(e);
				}
			}
		}).catch((err: any) => {
			reject(new Error(err?.message || 'Payment failed'));
		});
	});
}
