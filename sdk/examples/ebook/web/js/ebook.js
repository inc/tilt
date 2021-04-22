var EBOOK = new function() {

	var self = this;

	this.init = function() {

		$(document).ready(function() {
			$.getJSON("/config.json", function(config) {
				TILT.set_wallet_id(config['wallet_id']);
				self.config = config;
				for (var sku in config['skus']) {
					var book = config['skus'][sku];
					$('#sel-book').append('<option value="' + sku +'">' +
						book['title'] + ' ($' + book['price'].toFixed(2) +
						' USD)</option>')
				}
				$("#sel-book option:first").attr('selected','selected');
      		$('#sel-currency').change();
			});
		});

		$('#sel-book').change(function() {
     		$('#sel-currency').change();
		});

		$('#sel-currency').change(function() {
			var currency = $('#sel-currency :selected').val();
			TILT.quote(currency + 'usd', function(res) {
				var sku = $('#sel-book :selected').val();
				var priceusd = self.config['skus'][sku]['price'];
				var price = (priceusd / res['price']).toFixed(10);
				$('#lbl-price').text(price + " " + currency.toUpperCase());
			});
		});

		$('#btn-buy').click(function() {
			var sku = $('#sel-book :selected').val();
			var book = self.config['skus'][sku];
			if (!$('#txt-email').val()) {
				alert("Please enter an email address so we can deliver the book!");
				return;
			}
			var currency = $('#sel-currency :selected').val();
			var meta = {
				'type': 'ebook',
				'title': book['title'],
				'sku': sku,
				'email': $('#txt-email').val(),
			};
			$('#lbl-help').text("Generating a new address, one second ...");
			$('#sel-currency').hide();
			$('#sel-book').hide();
			$('#txt-email').hide();
			$('#btn-buy').hide();
			TILT.create_address(currency, meta, function(res) {
				if (res['ok']) {
					$('#txt-address').text(res['address']);
					$('#txt-address').removeClass('d-none');
					$('#lbl-help').text("Please send your payment to the above " +
						currency.toUpperCase() + " address.")
				} else {
					alert("Something went wrong, please try again later.");
				}
			});
		});

	};

	self.init();
	
};
