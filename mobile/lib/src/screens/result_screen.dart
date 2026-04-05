import 'package:flutter/material.dart';

import '../models/ingredient_check_models.dart';
import '../models/product_lookup_models.dart';

typedef ResultScreenAction = Future<void> Function(BuildContext context);

class ResultScreen extends StatelessWidget {
  const ResultScreen({
    super.key,
    required this.title,
    required this.resultStatus,
    required this.explanation,
    required this.matchedIngredients,
    this.submittedLabel,
    this.submittedText,
    this.productName,
    this.brandName,
    this.barcode,
    this.coverageStatus,
    this.fallbackActionLabel,
    this.onFallbackAction,
  });

  factory ResultScreen.forIngredientCheck({
    Key? key,
    required String ingredientText,
    required IngredientCheckResult result,
  }) {
    return ResultScreen(
      key: key,
      title: 'Result',
      resultStatus: result.status,
      explanation: result.explanation,
      matchedIngredients: result.matchedIngredients,
      submittedLabel: 'Submitted Ingredients',
      submittedText: ingredientText,
    );
  }

  factory ResultScreen.forProductLookup({
    Key? key,
    required String barcode,
    required ProductLookupResult result,
    String? fallbackActionLabel,
    ResultScreenAction? onFallbackAction,
  }) {
    return ResultScreen(
      key: key,
      title: 'Lookup Result',
      resultStatus: result.assessmentResult ?? 'cannot_verify',
      explanation: result.explanation,
      matchedIngredients: result.matchedIngredients,
      submittedLabel: result.ingredientText == null ? null : 'Ingredient Text',
      submittedText: result.ingredientText,
      productName: result.product?.productName,
      brandName: result.product?.brandName,
      barcode: result.product?.barcode.isNotEmpty == true
          ? result.product?.barcode
          : barcode,
      coverageStatus: result.product?.ingredientCoverageStatus,
      fallbackActionLabel: fallbackActionLabel,
      onFallbackAction: onFallbackAction,
    );
  }

  final String title;
  final String resultStatus;
  final String explanation;
  final List<MatchedIngredient> matchedIngredients;
  final String? submittedLabel;
  final String? submittedText;
  final String? productName;
  final String? brandName;
  final String? barcode;
  final String? coverageStatus;
  final String? fallbackActionLabel;
  final ResultScreenAction? onFallbackAction;

  bool get _hasProductDetails =>
      productName != null ||
      brandName != null ||
      barcode != null ||
      coverageStatus != null;

  bool get _isLookupResult => title == 'Lookup Result';

  int get _matchCount => matchedIngredients.length;

  Color _statusColor() {
    switch (resultStatus) {
      case 'contains_nut_ingredient':
        return const Color(0xFFC53B33);
      case 'possible_nut_derived_ingredient':
        return const Color(0xFFC17A00);
      case 'no_nut_ingredient_found':
        return const Color(0xFF2E7D32);
      default:
        return const Color(0xFF6B7280);
    }
  }

  Color _statusSurfaceColor() {
    switch (resultStatus) {
      case 'contains_nut_ingredient':
        return const Color(0xFFFDE8E6);
      case 'possible_nut_derived_ingredient':
        return const Color(0xFFFFF3DB);
      case 'no_nut_ingredient_found':
        return const Color(0xFFE6F4EA);
      default:
        return const Color(0xFFF1F3F5);
    }
  }

  IconData _statusIcon() {
    switch (resultStatus) {
      case 'contains_nut_ingredient':
        return Icons.warning_rounded;
      case 'possible_nut_derived_ingredient':
        return Icons.error_outline_rounded;
      case 'no_nut_ingredient_found':
        return Icons.check_circle_rounded;
      default:
        return Icons.help_outline_rounded;
    }
  }

  String _decisionLabel() {
    switch (resultStatus) {
      case 'contains_nut_ingredient':
        return 'Avoid';
      case 'possible_nut_derived_ingredient':
        return 'Use caution';
      case 'no_nut_ingredient_found':
        return 'Looks clear';
      default:
        return 'Cannot confirm';
    }
  }

  String _statusLabel() {
    switch (resultStatus) {
      case 'contains_nut_ingredient':
        return 'Contains nut ingredient';
      case 'possible_nut_derived_ingredient':
        return 'Possible nut-derived ingredient';
      case 'no_nut_ingredient_found':
        return 'No nut ingredient found';
      default:
        return 'Cannot verify';
    }
  }

  String _statusCaption() {
    switch (resultStatus) {
      case 'contains_nut_ingredient':
        return 'A known nut-linked ingredient was matched.';
      case 'possible_nut_derived_ingredient':
        return 'At least one ingredient may be nut-derived or too generic to verify safely.';
      case 'no_nut_ingredient_found':
        return 'The current ingredient list did not match any nut-linked rules.';
      default:
        return 'The ingredient data was missing, incomplete, or too vague to assess confidently.';
    }
  }

  String _statusActionHint() {
    switch (resultStatus) {
      case 'contains_nut_ingredient':
        return 'Avoid this product unless you have separate confirmation it is safe for your allergy profile.';
      case 'possible_nut_derived_ingredient':
        return 'Review the flagged ingredients carefully before using this product.';
      case 'no_nut_ingredient_found':
        return 'No nut-linked ingredients were flagged in the ingredient list that was checked.';
      default:
        return 'Treat this result as incomplete and verify the full ingredient list before using the product.';
    }
  }

  String _matchSummary() {
    if (_matchCount == 0) {
      return 'No flagged ingredients';
    }
    if (_matchCount == 1) {
      return '1 flagged ingredient';
    }
    return '$_matchCount flagged ingredients';
  }

  String _coverageLabel() {
    switch (coverageStatus) {
      case 'complete':
        return 'Ingredient list available';
      case 'partial':
        return 'Partial ingredient coverage';
      case 'missing':
        return 'No ingredient list returned';
      case 'unknown':
        return 'Ingredient coverage unknown';
      default:
        return coverageStatus ?? 'Unknown';
    }
  }

  String _primaryActionLabel() {
    return _isLookupResult ? 'Scan Again' : 'Check Another Ingredient List';
  }

  Widget _sectionCard({
    required BuildContext context,
    required String title,
    required Widget child,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE3E0D8)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x12000000),
            blurRadius: 12,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }

  Widget _labeledDetail({
    required BuildContext context,
    required String label,
    required String value,
    IconData? icon,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (icon != null) ...[
            Icon(
              icon,
              size: 18,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
            const SizedBox(width: 10),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _metaChip({
    required BuildContext context,
    required IconData icon,
    required String label,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.18),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: Colors.white.withOpacity(0.24)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: Colors.white),
          const SizedBox(width: 8),
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
          ),
        ],
      ),
    );
  }

  Widget _fallbackActionCard(BuildContext context) {
    return _sectionCard(
      context: context,
      title: 'Need a Better Result?',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'If this barcode did not return a usable ingredient list, you can save ingredients from the product label and reuse them on future scans.',
            style:
                Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.4),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              key: const Key('result-fallback-action'),
              onPressed: () async {
                if (onFallbackAction == null) {
                  return;
                }
                await onFallbackAction!(context);
              },
              icon: const Icon(Icons.note_add_rounded),
              label: Text(fallbackActionLabel!),
            ),
          ),
        ],
      ),
    );
  }

  Widget _productSummary(BuildContext context) {
    final headline = productName ?? 'Product not identified';

    return _sectionCard(
      context: context,
      title: 'Product',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _labeledDetail(
            context: context,
            label: 'Product name',
            value: headline,
            icon: Icons.inventory_2_rounded,
          ),
          if (brandName != null) ...[
            const SizedBox(height: 10),
            _labeledDetail(
              context: context,
              label: 'Brand',
              value: brandName!,
              icon: Icons.sell_rounded,
            ),
          ],
          if (barcode != null) ...[
            const SizedBox(height: 10),
            _labeledDetail(
              context: context,
              label: 'Barcode',
              value: barcode!,
              icon: Icons.qr_code_rounded,
            ),
          ],
          if (coverageStatus != null) ...[
            const SizedBox(height: 10),
            _labeledDetail(
              context: context,
              label: 'Ingredient coverage',
              value: _coverageLabel(),
              icon: Icons.fact_check_rounded,
            ),
          ],
        ],
      ),
    );
  }

  Widget _detailPill({
    required BuildContext context,
    required IconData icon,
    required String label,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon,
              size: 18, color: Theme.of(context).colorScheme.onSurfaceVariant),
          const SizedBox(width: 8),
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
        ],
      ),
    );
  }

  Widget _matchedIngredientCard(BuildContext context, MatchedIngredient match) {
    final statusColor = _statusColor();
    final textTheme = Theme.of(context).textTheme;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _statusSurfaceColor(),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: statusColor.withOpacity(0.28), width: 1.4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: statusColor,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.priority_high_rounded,
                    color: Colors.white),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      match.originalText,
                      style: textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Flagged ingredient',
                      style: textTheme.labelLarge?.copyWith(
                        color: statusColor,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    if (match.normalizedName.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        'Normalized as ${match.normalizedName}',
                        style: textTheme.bodyMedium?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              if (match.nutSource.isNotEmpty)
                _detailPill(
                  context: context,
                  icon: Icons.eco_rounded,
                  label: match.nutSource,
                ),
              if (match.confidence.isNotEmpty)
                _detailPill(
                  context: context,
                  icon: Icons.analytics_rounded,
                  label: match.confidence,
                ),
            ],
          ),
          if (match.reason.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              match.reason,
              style: textTheme.bodyMedium?.copyWith(height: 1.35),
            ),
          ],
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final statusColor = _statusColor();
    final statusSurfaceColor = _statusSurfaceColor();
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 120),
        children: [
          Container(
            key: const Key('result-status-banner'),
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: statusColor,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: statusColor.withOpacity(0.24),
                  blurRadius: 18,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.16),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    _decisionLabel().toUpperCase(),
                    style: textTheme.labelLarge?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w900,
                      letterSpacing: 0.8,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(_statusIcon(), color: Colors.white, size: 32),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _statusLabel(),
                            style: textTheme.headlineSmall?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            _statusCaption(),
                            style: textTheme.bodyLarge?.copyWith(
                              color: Colors.white.withOpacity(0.92),
                              height: 1.35,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.14),
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(
                                color: Colors.white.withOpacity(0.18),
                              ),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'What to do next',
                                  style: textTheme.labelLarge?.copyWith(
                                    color: Colors.white,
                                    fontWeight: FontWeight.w800,
                                    letterSpacing: 0.3,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  _statusActionHint(),
                                  style: textTheme.bodyMedium?.copyWith(
                                    color: Colors.white.withOpacity(0.94),
                                    height: 1.35,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    _metaChip(
                      context: context,
                      icon: Icons.list_alt_rounded,
                      label: _matchSummary(),
                    ),
                    if (coverageStatus != null)
                      _metaChip(
                        context: context,
                        icon: Icons.fact_check_rounded,
                        label: _coverageLabel(),
                      ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          _sectionCard(
            context: context,
            title: 'Quick Summary',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _labeledDetail(
                  context: context,
                  label: 'Assessment',
                  value: _statusLabel(),
                  icon: _statusIcon(),
                ),
                const SizedBox(height: 10),
                _labeledDetail(
                  context: context,
                  label: 'Matched ingredients',
                  value: _matchSummary(),
                  icon: Icons.list_alt_rounded,
                ),
              ],
            ),
          ),
          if (fallbackActionLabel != null && onFallbackAction != null) ...[
            const SizedBox(height: 18),
            _fallbackActionCard(context),
          ],
          const SizedBox(height: 18),
          if (_hasProductDetails) ...[
            _productSummary(context),
            const SizedBox(height: 18),
          ],
          _sectionCard(
            context: context,
            title: 'Why This Result',
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: statusSurfaceColor,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                explanation,
                style: textTheme.bodyLarge?.copyWith(height: 1.45),
              ),
            ),
          ),
          const SizedBox(height: 18),
          _sectionCard(
            context: context,
            title: matchedIngredients.isEmpty
                ? 'Matched Ingredients'
                : 'Flagged Ingredients',
            child: matchedIngredients.isEmpty
                ? Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color:
                          Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(
                      resultStatus == 'no_nut_ingredient_found'
                          ? 'No nut-linked ingredients were flagged for this result.'
                          : 'No matched ingredients returned.',
                      style: textTheme.bodyMedium,
                    ),
                  )
                : Column(
                    children: [
                      for (var i = 0; i < matchedIngredients.length; i++) ...[
                        _matchedIngredientCard(context, matchedIngredients[i]),
                        if (i != matchedIngredients.length - 1)
                          const SizedBox(height: 12),
                      ],
                    ],
                  ),
          ),
          if (submittedText != null && submittedLabel != null) ...[
            const SizedBox(height: 18),
            _sectionCard(
              context: context,
              title: submittedLabel!,
              child: SelectableText(
                submittedText!,
                style: textTheme.bodyMedium?.copyWith(height: 1.4),
              ),
            ),
          ],
        ],
      ),
      bottomNavigationBar: SafeArea(
        minimum: const EdgeInsets.fromLTRB(20, 12, 20, 16),
        child: Row(
          children: [
            Expanded(
              flex: 3,
              child: FilledButton.icon(
                key: const Key('result-primary-action'),
                onPressed: () => Navigator.of(context).pop(),
                icon: Icon(_isLookupResult
                    ? Icons.qr_code_scanner_rounded
                    : Icons.refresh_rounded),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                label: Text(_primaryActionLabel()),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              flex: 2,
              child: OutlinedButton.icon(
                onPressed: () => Navigator.of(context).maybePop(),
                icon: const Icon(Icons.arrow_back_rounded),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                label: const Text('Back'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
