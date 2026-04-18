import 'package:flutter/foundation.dart';

class ScanHistoryRefreshController extends ChangeNotifier {
  int _revision = 0;

  int get revision => _revision;

  void markChanged() {
    _revision += 1;
    notifyListeners();
  }
}
