<?php
/**
 * Plugin Name
 *
 * @package           Tilt
 * @author            Lone Dynamics
 * @copyright         2021 Lone Dynamics Corporation
 * @license           LDOL
 *
 * @wordpress-plugin
 * Plugin Name:       Tilt Cryptocurrency Payments
 * Plugin URI:        https://github.com/inc/tilt/blob/main/sdk/woocommerce
 * Description:       Accept cryptocurrency payments directly into your wallet.
 * Version:           1.0.0
 * Requires at least: 5.2
 * Requires PHP:      7.4
 * Author:            Lone Dynamics
 * Author URI:        https://lonedynamics.com
 * License:           Lone Dynamics Open License
 * License URI:       https://github.com/inc/tilt/blob/main/LICENSE.md
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}

add_action( 'plugins_loaded', 'tilt_init_gateway_class' );

function tilt_add_gateway_class( $methods ) {
	$methods[] = 'WC_Gateway_Tilt'; 
	return $methods;
}

add_filter( 'woocommerce_payment_gateways', 'tilt_add_gateway_class' );

// ---

function tilt_init_gateway_class() {

if ( ! class_exists( 'WC_Payment_Gateway' ) ) return;

class WC_Gateway_Tilt extends WC_Payment_Gateway {

	/**
	 * Constructor for the gateway.
	 */
	public function __construct() {
		$this->id                 = 'tilt';
		$this->icon               = apply_filters( 'woocommerce_tilt_icon', 'https://tilt.cash/images/tilt.png' );
		$this->has_fields         = true;
		$this->method_title       = _x( 'Cryptocurrency', 'Crypto payment method', 'woocommerce' );
		$this->method_description = __( 'Take payments via cryptocurrency using the Tilt platform.', 'woocommerce' );

		// Load the settings.
		$this->init_form_fields();
		$this->init_settings();

		// Define user set variables.
		$this->title        = $this->get_option( 'title' );
		$this->description  = $this->get_option( 'description' );

		// Actions.
		add_action( 'woocommerce_update_options_payment_gateways_' . $this->id, array( $this, 'process_admin_options' ) );
		add_action( 'woocommerce_thankyou_tilt', array( $this, 'thankyou_page' ) );

		// Customer Emails.
		add_action( 'woocommerce_email_before_order_table', array( $this, 'email_instructions' ), 10, 3 );
	}

   public function payment_fields() {

		echo $this->description . '<br/></br>';

		woocommerce_form_field( 'crypto_currency', array(
			'type'          => 'select',
			'class'         => array('form-row-wide'),
			'label'         => __('Select a payment currency'),
			'required'    => true,
			'options'     => array(
				'BTC' => __('Bitcoin (BTC)'),
				'LTC' => __('Litecoin (LTC)'),
				'DOGE' => __('Dogecoin (DOGE)'),
			),
			'default' => 'BTC'));

   }

   public function generate_instructions($order) {

		$addr = $order->get_meta('crypto_address');
		$currency = $order->get_meta('crypto_currency');
		$total = $order->get_meta('crypto_total');

		$instructions =
			'<h2>Payment Details</h2>' .
			'Please send a payment of <b>' . $total . '</b> ' . $currency .
			' to the following address:<br/><b>' . $addr . '</b><br/><br/>' .
			'<i>Note: Depending on the currency used it may take over an hour ' .
			'to confirm your payment. We will send an update once your payment ' .
			'is confirmed and your order is being processed.</i>';

		return $instructions;
   }

	/**
	 * Initialise Gateway Settings Form Fields.
	 */
	public function init_form_fields() {

		$this->form_fields = array(
			'enabled'      => array(
				'title'   => __( 'Enable/Disable', 'woocommerce' ),
				'type'    => 'checkbox',
				'label'   => __( 'Enable crypto payments', 'woocommerce' ),
				'default' => 'no',
			),
			'title'        => array(
				'title'       => __( 'Title', 'woocommerce' ),
				'type'        => 'text',
				'description' => __( 'This controls the title which the user sees during checkout.', 'woocommerce' ),
				'default'     => _x( 'Cryptocurrency', 'Crypto payment method', 'woocommerce' ),
				'desc_tip'    => true,
			),
			'description'  => array(
				'title'       => __( 'Description', 'woocommerce' ),
				'type'        => 'textarea',
				'description' => __( 'Payment method description that the customer will see on your checkout.', 'woocommerce' ),
				'default'     => __( 'Send a crypto payment directly to us.', 'woocommerce' ),
				'desc_tip'    => true,
			),
			'wallet'        => array(
				'title'       => __( 'Tilt Wallet ID', 'woocommerce' ),
				'type'        => 'text',
				'description' => __( 'Enter your Tilt wallet ID.', 'woocommerce' ),
				'default'     => '',
				'desc_tip'    => true,
			),
		);
	}

	/**
	 * Output for the order received page.
	 */
	public function thankyou_page($order_id) {
		$order = wc_get_order($order_id);
		echo wp_kses_post( wpautop( wptexturize( $this->generate_instructions($order) ) ) );
	}

	/**
	 * Add content to the WC emails.
	 *
	 * @access public
	 * @param WC_Order $order Order object.
	 * @param bool     $sent_to_admin Sent to admin.
	 * @param bool     $plain_text Email format: plain text or HTML.
	 */
	public function email_instructions( $order, $sent_to_admin, $plain_text = false ) {
		$this->tilt_create_order($order);
		echo wp_kses_post( wpautop( wptexturize( $this->generate_instructions($order) ) ) . PHP_EOL );
	}

   public function tilt_create_order($order) {

		$total = $order->get_total();
		$currency = $order->get_currency();

		$crypto_currency = $_POST['crypto_currency'];

		$sym = $crypto_currency . $currency;

		$req = wp_remote_post("https://tilt.cash/api/v1/quote", array(
			'headers' =>
				array('Content-Type' => 'application/json; charset=utf-8'),
			'body' => json_encode(array('sym' => $sym)),
			'method' => 'POST',
			'data_format' => 'body',
		));

		$quote = json_decode(wp_remote_retrieve_body($req));
		$crypto_total = $total / $quote->price;

		$wallet = $this->get_option('wallet');
		
		$req = wp_remote_post("https://tilt.cash/api/v1/create_address", array(
			'headers' =>
				array('Content-Type' => 'application/json; charset=utf-8'),
			'body' => json_encode(array('wallet' => $wallet,
				'currency' => $crypto_currency,
				'meta' => array(
					'type' => 'woocommerce',
					'store_name' => get_bloginfo('name'),
					'order_id' => $order_id,
					'order_quoted' => $crypto_total,
					'order_currency' => $currency,
					'order_total' => $total))),
			'method' => 'POST',
			'data_format' => 'body',
		));

		$res = json_decode(wp_remote_retrieve_body($req));
		$addr = $res->address;

		$order->add_meta_data('crypto_address', $addr, true);
		$order->add_meta_data('crypto_currency', $_POST['crypto_currency'], true);
		$order->add_meta_data('crypto_total', $crypto_total, true);
		$order->save();
   }

	/**
	 * Process the payment and return the result.
	 *
	 * @param int $order_id Order ID.
	 * @return array
	 */
	public function process_payment( $order_id ) {

		$order = wc_get_order( $order_id );

		if ( $order->get_total() > 0 ) {
			// Mark as on-hold (we're awaiting the tilt).
			$order->update_status( apply_filters( 'woocommerce_tilt_process_payment_order_status', 'on-hold', $order ), _x( 'Awaiting crypto payment', 'Crypto payment method', 'woocommerce' ) );
		} else {
			$order->payment_complete();
		}

		// Remove cart.
		WC()->cart->empty_cart();

		// Return thankyou redirect.
		return array(
			'result'   => 'success',
			'redirect' => $this->get_return_url( $order ),
		);
	}
}

}

// ---

function tilt_cron_schedule( $schedules ) {
	$schedules['every_fifteen_minutes'] = array(
		'interval' => 900,
		'display'  => __( 'Every 15 minutes' ),
	);
	return $schedules;
}

add_filter( 'cron_schedules', 'tilt_cron_schedule' );
add_action( 'tilt_check_payments_hook', 'tilt_check_payments' );

if ( ! wp_next_scheduled( 'tilt_check_payments_hook' ) ) {
	wp_schedule_event( time(), 'every_fifteen_minutes',
		'tilt_check_payments_hook' );
}

function tilt_check_payments() {

	$on_hold_orders = wc_get_orders( array(
		'status' => 'on-hold',
	) );

	foreach ($on_hold_orders as $order) {

		$order_id = $order->get_id();
		$addr = $order->get_meta("crypto_address");
		$currency = $order->get_meta("crypto_currency");
		$order_total = $order->get_meta("crypto_total");

		if ( ! $addr ) continue;
		if ( ! $currency ) continue;
		if ( ! $order_total ) continue;

		$req = wp_remote_post("https://tilt.cash/api/v1/balance_address", array(
			'headers' =>
				array('Content-Type' => 'application/json; charset=utf-8'),
			'body' => json_encode(array(
				'currency' => $currency,
				'address' => $addr )),
			'method' => 'POST',
			'data_format' => 'body',
		));

		$res = json_decode(wp_remote_retrieve_body($req));
		$balance = $res->balance;

		if ( $balance >= $order_total ) {
			$order->set_status('processing');
			$order->save();
		}

	}

}
