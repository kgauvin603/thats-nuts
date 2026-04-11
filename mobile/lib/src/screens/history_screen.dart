import 'package:flutter/material.dart';

import '../brand.dart';
import '../models/scan_history_models.dart';
import '../services/thats_nuts_api_client.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({
    super.key,
    required this.apiClient,
  });

  static const routeName = '/history';

  final ThatsNutsApiClient apiClient;

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  bool _isLoading = true;
  bool _loadedSuccessfully = false;
  String? _errorMessage;
  List<ScanHistoryItem> _items = const [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await widget.apiClient.fetchScanHistory();
      if (!mounted) {
        return;
      }
      setState(() {
        _loadedSuccessfully = true;
        _items = response.items;
      });
    } on ThatsNutsApiException catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loadedSuccessfully = false;
        _items = const [];
        _errorMessage = error.message;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loadedSuccessfully = false;
        _items = const [];
        _errorMessage = 'Something went wrong while loading scan history.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Color _statusColor(BuildContext context, String status) {
    switch (status) {
      case 'contains_nut_ingredient':
        return BrandColors.danger;
      case 'possible_nut_derived_ingredient':
        return BrandColors.warning;
      case 'no_nut_ingredient_found':
        return BrandColors.success;
      default:
        return Theme.of(context).colorScheme.secondary;
    }
  }

  Color _statusSurfaceColor(String status) {
    switch (status) {
      case 'contains_nut_ingredient':
        return BrandColors.dangerSurface;
      case 'possible_nut_derived_ingredient':
        return BrandColors.warningSurface;
      case 'no_nut_ingredient_found':
        return BrandColors.successSurface;
      default:
        return BrandColors.neutralSurface;
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'contains_nut_ingredient':
        return 'Nut ingredient found';
      case 'possible_nut_derived_ingredient':
        return 'Possible nut-derived ingredient';
      case 'no_nut_ingredient_found':
        return 'No nut ingredient found';
      default:
        return 'Cannot verify';
    }
  }

  String _scanTypeLabel(String scanType) {
    switch (scanType) {
      case 'barcode_lookup':
        return 'Barcode lookup';
      case 'barcode_enrichment':
        return 'Barcode enrichment';
      default:
        return 'Manual check';
    }
  }

  String _formatCreatedAt(DateTime createdAt) {
    final local = createdAt.toLocal();
    final month = local.month.toString().padLeft(2, '0');
    final day = local.day.toString().padLeft(2, '0');
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');
    return '${local.year}-$month-$day $hour:$minute';
  }

  String _entryTitle(ScanHistoryItem item) {
    if (item.productName != null && item.productName!.trim().isNotEmpty) {
      return item.productName!;
    }
    if (item.scanType == 'barcode_enrichment') {
      return 'Barcode enrichment';
    }
    if (item.scanType == 'barcode_lookup') {
      return 'Barcode lookup';
    }
    return 'Manual ingredient check';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Recent History'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadHistory,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              'Recent ingredient checks and barcode lookups from the backend.',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            if (_isLoading)
              const Padding(
                padding: EdgeInsets.only(top: 40),
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              )
            else if (_errorMessage != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Could not load history',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(_errorMessage!),
                      const SizedBox(height: 12),
                      FilledButton(
                        onPressed: _loadHistory,
                        child: const Text('Try Again'),
                      ),
                    ],
                  ),
                ),
              )
            else if (_loadedSuccessfully && _items.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    'No scans yet. Run a manual ingredient check or barcode lookup first.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ),
              )
            else
              ..._items.map(
                (item) {
                  final statusColor =
                      _statusColor(context, item.assessmentStatus);
                  final statusSurfaceColor =
                      _statusSurfaceColor(item.assessmentStatus);

                  return Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    clipBehavior: Clip.antiAlias,
                    child: IntrinsicHeight(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Container(width: 8, color: statusColor),
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Wrap(
                                    spacing: 8,
                                    runSpacing: 8,
                                    children: [
                                      Chip(
                                        label:
                                            Text(_scanTypeLabel(item.scanType)),
                                        visualDensity: VisualDensity.compact,
                                      ),
                                      Chip(
                                        label: Text(
                                          _statusLabel(item.assessmentStatus),
                                        ),
                                        visualDensity: VisualDensity.compact,
                                        backgroundColor: statusSurfaceColor,
                                        side: BorderSide(
                                          color: statusColor.withOpacity(0.22),
                                        ),
                                        labelStyle: TextStyle(
                                          color: statusColor,
                                          fontWeight: FontWeight.w800,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),
                                  Text(
                                    _entryTitle(item),
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleMedium
                                        ?.copyWith(
                                          fontWeight: FontWeight.w800,
                                        ),
                                  ),
                                  if (item.brandName != null) ...[
                                    const SizedBox(height: 4),
                                    Text(
                                      item.brandName!,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyMedium
                                          ?.copyWith(
                                            color: Theme.of(context)
                                                .colorScheme
                                                .onSurfaceVariant,
                                          ),
                                    ),
                                  ],
                                  const SizedBox(height: 10),
                                  Container(
                                    width: double.infinity,
                                    padding: const EdgeInsets.all(14),
                                    decoration: BoxDecoration(
                                      color: statusSurfaceColor,
                                      borderRadius: BorderRadius.circular(16),
                                      border: Border.all(
                                        color: statusColor.withOpacity(0.18),
                                      ),
                                    ),
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          _statusLabel(item.assessmentStatus),
                                          style: Theme.of(context)
                                              .textTheme
                                              .titleSmall
                                              ?.copyWith(
                                                color: statusColor,
                                                fontWeight: FontWeight.w800,
                                              ),
                                        ),
                                        if (item.explanation != null) ...[
                                          const SizedBox(height: 6),
                                          Text(
                                            item.explanation!,
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodyMedium
                                                ?.copyWith(height: 1.35),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ),
                                  if (item.barcode != null) ...[
                                    const SizedBox(height: 10),
                                    Text(
                                      'Barcode: ${item.barcode}',
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodySmall
                                          ?.copyWith(
                                            fontWeight: FontWeight.w700,
                                          ),
                                    ),
                                  ],
                                  if (item.submittedIngredientText != null &&
                                      item.submittedIngredientText!
                                          .trim()
                                          .isNotEmpty) ...[
                                    const SizedBox(height: 10),
                                    Text(
                                      item.submittedIngredientText!,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyMedium,
                                      maxLines: 3,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ],
                                  const SizedBox(height: 10),
                                  Text(
                                    'Checked: ${_formatCreatedAt(item.createdAt)}',
                                    style: Theme.of(context)
                                        .textTheme
                                        .bodySmall
                                        ?.copyWith(
                                          color: Theme.of(context)
                                              .colorScheme
                                              .onSurfaceVariant,
                                        ),
                                  ),
                                  if (item.matchedIngredientSummary !=
                                      null) ...[
                                    const SizedBox(height: 8),
                                    Text(
                                      'Matched: ${item.matchedIngredientSummary}',
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodySmall
                                          ?.copyWith(
                                            color: statusColor,
                                            fontWeight: FontWeight.w700,
                                          ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }
}
