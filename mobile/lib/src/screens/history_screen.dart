import 'package:flutter/material.dart';

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
        _items = response.items;
      });
    } on ThatsNutsApiException catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _errorMessage = error.message;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
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
        return const Color(0xFFAA3A2A);
      case 'possible_nut_derived_ingredient':
        return const Color(0xFF946200);
      case 'no_nut_ingredient_found':
        return const Color(0xFF2F6B3A);
      default:
        return Theme.of(context).colorScheme.secondary;
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
    return scanType == 'barcode_lookup' ? 'Barcode lookup' : 'Manual check';
  }

  bool _isManualEnrichment(ScanHistoryItem item) {
    return item.scanType == 'barcode_lookup' &&
        (item.productSource == 'manual_entry' ||
            item.productSource == 'text_scan');
  }

  String _sourceLabel(ScanHistoryItem item) {
    if (_isManualEnrichment(item)) {
      return 'Manual enrichment';
    }
    return _scanTypeLabel(item.scanType);
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
    if (_isManualEnrichment(item)) {
      return 'Barcode enriched with manual ingredients';
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
            else if (_items.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    'No scan history yet. Run a manual ingredient check or barcode lookup first.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ),
              )
            else
              ..._items.map(
                (item) => Card(
                  margin: const EdgeInsets.only(bottom: 12),
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
                              label: Text(_sourceLabel(item)),
                              visualDensity: VisualDensity.compact,
                            ),
                            Chip(
                              label: Text(_statusLabel(item.assessmentStatus)),
                              visualDensity: VisualDensity.compact,
                              backgroundColor: _statusColor(
                                context,
                                item.assessmentStatus,
                              ).withOpacity(0.12),
                              side: BorderSide.none,
                              labelStyle: TextStyle(
                                color: _statusColor(
                                    context, item.assessmentStatus),
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _entryTitle(item),
                          style:
                              Theme.of(context).textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.w700,
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
                        if (item.barcode != null)
                          Text('Barcode: ${item.barcode}'),
                        if (_isManualEnrichment(item)) ...[
                          const SizedBox(height: 8),
                          Text(
                            'Saved from manually captured ingredients for this barcode.',
                            style:
                                Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: Theme.of(context)
                                          .colorScheme
                                          .onSurfaceVariant,
                                      fontWeight: FontWeight.w600,
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
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                        Text('Checked: ${_formatCreatedAt(item.createdAt)}'),
                        if (item.explanation != null) ...[
                          const SizedBox(height: 10),
                          Text(
                            item.explanation!,
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                        if (item.matchedIngredientSummary != null) ...[
                          const SizedBox(height: 10),
                          Text(
                            'Matched: ${item.matchedIngredientSummary}',
                            style:
                                Theme.of(context).textTheme.bodySmall?.copyWith(
                                      fontWeight: FontWeight.w600,
                                    ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
