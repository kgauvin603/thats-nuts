import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../brand.dart';
import '../models/allergy_profile.dart';
import '../models/product_lookup_models.dart';
import '../services/scan_history_refresh_controller.dart';
import '../services/thats_nuts_api_client.dart';
import 'barcode_enrichment_screen.dart';
import 'barcode_input_screen.dart';
import 'result_screen.dart';

class BarcodeScannerScreen extends StatefulWidget {
  const BarcodeScannerScreen({
    super.key,
    required this.apiClient,
    required this.allergyProfile,
    required this.historyRefreshController,
    this.scannerPreview,
  });

  static const routeName = '/barcode-scanner';

  final ThatsNutsApiClient apiClient;
  final AllergyProfile allergyProfile;
  final ScanHistoryRefreshController historyRefreshController;
  final Widget? scannerPreview;

  @override
  State<BarcodeScannerScreen> createState() => _BarcodeScannerScreenState();
}

class _BarcodeScannerScreenState extends State<BarcodeScannerScreen> {
  final MobileScannerController _controller = MobileScannerController(
    detectionSpeed: DetectionSpeed.noDuplicates,
    formats: const [
      BarcodeFormat.ean13,
      BarcodeFormat.ean8,
      BarcodeFormat.upcA,
      BarcodeFormat.upcE,
    ],
  );

  bool _isHandlingScan = false;
  String? _errorMessage;
  String? _lastScannedBarcode;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _restartScanner() async {
    setState(() {
      _errorMessage = null;
      _lastScannedBarcode = null;
      _isHandlingScan = false;
    });

    try {
      await _controller.stop();
      await _controller.start();
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _errorMessage = 'Could not restart the camera scanner.';
      });
    }
  }

  Future<void> _handleBarcode(String barcode) async {
    if (_isHandlingScan) {
      return;
    }

    setState(() {
      _isHandlingScan = true;
      _errorMessage = null;
      _lastScannedBarcode = barcode;
    });

    try {
      await _controller.stop();
      final result = await widget.apiClient.lookupProduct(
        barcode,
        allergyProfile: widget.allergyProfile,
      );
      widget.historyRefreshController.markChanged();
      if (!mounted) {
        return;
      }
      await _openLookupResult(barcode, result);
      await _restartScanner();
    } on ThatsNutsApiException catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _errorMessage = error.message;
      });
      await _controller.start();
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _errorMessage =
            'Something went wrong while looking up the scanned barcode.';
      });
      await _controller.start();
    } finally {
      if (mounted) {
        setState(() {
          _isHandlingScan = false;
        });
      }
    }
  }

  Future<void> _openLookupResult(String barcode, ProductLookupResult result) {
    return Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => ResultScreen.forProductLookup(
          barcode: barcode,
          result: result,
          fallbackActionLabel: result.canAddIngredientsFallback
              ? 'Add Ingredients for This Barcode'
              : null,
          onFallbackAction: result.canAddIngredientsFallback
              ? (screenContext) => Navigator.of(screenContext).push(
                    MaterialPageRoute<void>(
                      builder: (context) => BarcodeEnrichmentScreen(
                        apiClient: widget.apiClient,
                        allergyProfile: widget.allergyProfile,
                        historyRefreshController:
                            widget.historyRefreshController,
                        barcode: barcode,
                        initialProductName: result.product?.productName,
                        initialBrandName: result.product?.brandName,
                      ),
                    ),
                  )
              : null,
        ),
      ),
    );
  }

  String _scannerStatusText(MobileScannerState state) {
    if (_isHandlingScan) {
      return _lastScannedBarcode == null
          ? 'Looking up product...'
          : 'Looking up $_lastScannedBarcode...';
    }
    if (state.error?.errorCode == MobileScannerErrorCode.permissionDenied) {
      return 'Camera permission is required to scan.';
    }
    if (state.error != null) {
      return 'Camera unavailable right now.';
    }
    if (state.isStarting) {
      return 'Starting camera...';
    }
    if (state.isRunning) {
      return 'Scanner ready. A successful scan opens the result screen.';
    }
    return 'Align a barcode inside the frame.';
  }

  Widget _buildScannerError(
    BuildContext context,
    MobileScannerException error,
  ) {
    final isPermissionError =
        error.errorCode == MobileScannerErrorCode.permissionDenied;
    final title =
        isPermissionError ? 'Camera permission needed' : 'Scanner unavailable';
    final body = isPermissionError
        ? 'Allow camera access in system settings, then return here to scan. You can still enter a barcode manually.'
        : error.errorDetails?.message?.isNotEmpty == true
            ? error.errorDetails!.message!
            : error.errorCode.message;

    return ColoredBox(
      color: BrandColors.ink,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Center(
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(body),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute<void>(
                          builder: (context) => BarcodeInputScreen(
                            apiClient: widget.apiClient,
                            allergyProfile: widget.allergyProfile,
                            historyRefreshController:
                                widget.historyRefreshController,
                          ),
                        ),
                      );
                    },
                    child: const Text('Enter Barcode Manually'),
                  ),
                  if (!isPermissionError) ...[
                    const SizedBox(height: 8),
                    OutlinedButton(
                      onPressed: _restartScanner,
                      child: const Text('Retry Camera'),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Barcode'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Point the camera at a UPC or EAN barcode.',
                    style: textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 10,
                    ),
                    decoration: BoxDecoration(
                      color: BrandColors.surfaceAlt,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: BrandColors.border),
                    ),
                    child: Text(
                      widget.allergyProfile.hasSelections
                          ? 'Profile: ${widget.allergyProfile.summary}'
                          : 'Profile: checking all supported nut-related ingredients.',
                      style: textTheme.bodySmall,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'The result opens automatically after a successful scan.',
                    style: textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 12),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(24),
                    child: AspectRatio(
                      aspectRatio: 3 / 4,
                      child: ValueListenableBuilder<MobileScannerState>(
                        valueListenable: _controller,
                        builder: (context, state, _) {
                          return Stack(
                            fit: StackFit.expand,
                            children: [
                              widget.scannerPreview ??
                                  MobileScanner(
                                    controller: _controller,
                                    errorBuilder: _buildScannerError,
                                    onDetect: (capture) {
                                      if (_isHandlingScan) {
                                        return;
                                      }

                                      for (final barcode in capture.barcodes) {
                                        final rawValue =
                                            barcode.rawValue?.trim();
                                        if (rawValue != null &&
                                            rawValue.isNotEmpty) {
                                          _handleBarcode(rawValue);
                                          return;
                                        }
                                      }
                                    },
                                  ),
                              IgnorePointer(
                                child: DecoratedBox(
                                  decoration: BoxDecoration(
                                    border: Border.all(
                                      color: BrandColors.border,
                                      width: 1.5,
                                    ),
                                  ),
                                  child: Center(
                                    child: Container(
                                      width: 240,
                                      height: 160,
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(24),
                                        border: Border.all(
                                          color: Colors.white.withOpacity(0.88),
                                          width: 3,
                                        ),
                                        gradient: LinearGradient(
                                          colors: [
                                            Colors.black.withOpacity(0.14),
                                            Colors.black.withOpacity(0.04),
                                          ],
                                          begin: Alignment.topCenter,
                                          end: Alignment.bottomCenter,
                                        ),
                                      ),
                                      alignment: Alignment.bottomCenter,
                                      padding: const EdgeInsets.all(12),
                                      child: Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.end,
                                        children: [
                                          Text(
                                            _scannerStatusText(state),
                                            textAlign: TextAlign.center,
                                            style:
                                                textTheme.bodyMedium?.copyWith(
                                              color: Colors.white,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                          if (_lastScannedBarcode != null &&
                                              !_isHandlingScan) ...[
                                            const SizedBox(height: 8),
                                            Text(
                                              'Last scan: $_lastScannedBarcode',
                                              textAlign: TextAlign.center,
                                              style:
                                                  textTheme.bodySmall?.copyWith(
                                                color: Colors.white
                                                    .withOpacity(0.92),
                                              ),
                                            ),
                                          ],
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  ValueListenableBuilder<MobileScannerState>(
                    valueListenable: _controller,
                    builder: (context, state, _) {
                      final torchUnavailable =
                          state.torchState == TorchState.unavailable;
                      final torchOn = state.torchState == TorchState.on;

                      return Wrap(
                        spacing: 12,
                        runSpacing: 12,
                        children: [
                          OutlinedButton.icon(
                            onPressed: (_isHandlingScan || torchUnavailable)
                                ? null
                                : () => _controller.toggleTorch(),
                            icon: Icon(torchOn
                                ? Icons.flash_on_rounded
                                : Icons.flash_off_rounded),
                            label: Text(torchOn ? 'Torch On' : 'Torch Off'),
                          ),
                          OutlinedButton.icon(
                            onPressed: _isHandlingScan ? null : _restartScanner,
                            icon: const Icon(Icons.center_focus_strong_rounded),
                            label: const Text('Retry Scanner'),
                          ),
                        ],
                      );
                    },
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'The camera is limited to UPC and EAN formats to match product lookup. If scanning is unavailable or permission is denied, use manual barcode entry instead.',
                    style: textTheme.bodyMedium,
                  ),
                  if (_errorMessage != null) ...[
                    const SizedBox(height: 12),
                    Card(
                      color: Theme.of(context).colorScheme.errorContainer,
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Lookup failed',
                              style: textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.w700,
                                color: Theme.of(context)
                                    .colorScheme
                                    .onErrorContainer,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              _errorMessage!,
                              style: TextStyle(
                                color: Theme.of(context)
                                    .colorScheme
                                    .onErrorContainer,
                              ),
                            ),
                            const SizedBox(height: 10),
                            Wrap(
                              spacing: 10,
                              runSpacing: 10,
                              children: [
                                FilledButton(
                                  onPressed: _restartScanner,
                                  child: const Text('Try Scanning Again'),
                                ),
                                OutlinedButton(
                                  onPressed: () {
                                    Navigator.of(context).push(
                                      MaterialPageRoute<void>(
                                        builder: (context) =>
                                            BarcodeInputScreen(
                                          apiClient: widget.apiClient,
                                          allergyProfile: widget.allergyProfile,
                                          historyRefreshController:
                                              widget.historyRefreshController,
                                        ),
                                      ),
                                    );
                                  },
                                  child: const Text('Enter Barcode Manually'),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute<void>(
                            builder: (context) => BarcodeInputScreen(
                              apiClient: widget.apiClient,
                              allergyProfile: widget.allergyProfile,
                              historyRefreshController:
                                  widget.historyRefreshController,
                            ),
                          ),
                        );
                      },
                      child: const Text('Enter Barcode Manually'),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Supported formats: UPC-A, UPC-E, EAN-8, EAN-13.',
                    style: textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
