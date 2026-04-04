import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/allergy_profile.dart';
import '../models/ingredient_check_models.dart';
import '../models/product_lookup_models.dart';
import '../models/scan_history_models.dart';

class ThatsNutsApiClient {
  ThatsNutsApiClient({
    http.Client? httpClient,
    String? baseUrl,
  })  : _httpClient = httpClient ?? http.Client(),
        _baseUrl = baseUrl ??
            const String.fromEnvironment(
              'API_BASE_URL',
              defaultValue: 'http://10.0.2.2:8002',
            );

  final http.Client _httpClient;
  final String _baseUrl;

  Future<IngredientCheckResult> checkIngredients(
    String ingredientText, {
    AllergyProfile? allergyProfile,
  }) async {
    final response = await _httpClient.post(
      Uri.parse('$_baseUrl/check-ingredients'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode(
        _buildRequestBody(
          {
            'ingredient_text': ingredientText,
          },
          allergyProfile,
        ),
      ),
    );

    if (response.statusCode != 200) {
      throw ThatsNutsApiException(
        'Backend request failed with status ${response.statusCode}.',
      );
    }

    final payload = jsonDecode(response.body) as Map<String, dynamic>;
    return IngredientCheckResult.fromJson(payload);
  }

  Future<ProductLookupResult> lookupProduct(
    String barcode, {
    AllergyProfile? allergyProfile,
  }) async {
    final response = await _httpClient.post(
      Uri.parse('$_baseUrl/lookup-product'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode(
        _buildRequestBody(
          {
            'barcode': barcode,
          },
          allergyProfile,
        ),
      ),
    );

    if (response.statusCode != 200) {
      throw ThatsNutsApiException(
        'Backend request failed with status ${response.statusCode}.',
      );
    }

    final payload = jsonDecode(response.body) as Map<String, dynamic>;
    return ProductLookupResult.fromJson(payload);
  }

  Future<ScanHistoryResponse> fetchScanHistory({int limit = 20}) async {
    final response = await _httpClient.get(
      Uri.parse('$_baseUrl/scan-history?limit=$limit'),
    );

    if (response.statusCode != 200) {
      throw ThatsNutsApiException(
        'Backend request failed with status ${response.statusCode}.',
      );
    }

    final payload = jsonDecode(response.body) as Map<String, dynamic>;
    return ScanHistoryResponse.fromJson(payload);
  }

  Map<String, dynamic> _buildRequestBody(
    Map<String, dynamic> payload,
    AllergyProfile? allergyProfile,
  ) {
    final profilePayload = allergyProfile?.toRequestJson();
    if (profilePayload == null) {
      return payload;
    }
    return {
      ...payload,
      'allergy_profile': profilePayload,
    };
  }
}

class ThatsNutsApiException implements Exception {
  const ThatsNutsApiException(this.message);

  final String message;

  @override
  String toString() => message;
}
