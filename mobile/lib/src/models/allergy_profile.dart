class AllergyProfile {
  const AllergyProfile({
    this.peanut = false,
    this.treeNuts = false,
    this.almond = false,
    this.walnut = false,
    this.cashew = false,
    this.pistachio = false,
    this.hazelnut = false,
    this.macadamia = false,
    this.brazilNut = false,
    this.pecan = false,
    this.coconut = false,
    this.shea = false,
    this.argan = false,
    this.kukui = false,
  });

  final bool peanut;
  final bool treeNuts;
  final bool almond;
  final bool walnut;
  final bool cashew;
  final bool pistachio;
  final bool hazelnut;
  final bool macadamia;
  final bool brazilNut;
  final bool pecan;
  final bool coconut;
  final bool shea;
  final bool argan;
  final bool kukui;

  static const fields = <AllergyProfileField>[
    AllergyProfileField(key: 'peanut', label: 'Peanut'),
    AllergyProfileField(key: 'treeNuts', label: 'Tree nuts'),
    AllergyProfileField(key: 'almond', label: 'Almond'),
    AllergyProfileField(key: 'walnut', label: 'Walnut'),
    AllergyProfileField(key: 'cashew', label: 'Cashew'),
    AllergyProfileField(key: 'pistachio', label: 'Pistachio'),
    AllergyProfileField(key: 'hazelnut', label: 'Hazelnut'),
    AllergyProfileField(key: 'macadamia', label: 'Macadamia'),
    AllergyProfileField(key: 'brazilNut', label: 'Brazil nut'),
    AllergyProfileField(key: 'pecan', label: 'Pecan'),
    AllergyProfileField(key: 'coconut', label: 'Coconut'),
    AllergyProfileField(key: 'shea', label: 'Shea'),
    AllergyProfileField(key: 'argan', label: 'Argan'),
    AllergyProfileField(key: 'kukui', label: 'Kukui'),
  ];

  bool get hasSelections => fields.any((field) => valueFor(field.key));

  List<String> get selectedLabels => [
        for (final field in fields)
          if (valueFor(field.key)) field.label,
      ];

  String get summary {
    final labels = selectedLabels;
    if (labels.isEmpty) {
      return 'All supported nut-related ingredients will be considered.';
    }
    if (labels.length <= 3) {
      return labels.join(', ');
    }
    return '${labels.take(3).join(', ')} +${labels.length - 3} more';
  }

  bool valueFor(String key) {
    switch (key) {
      case 'peanut':
        return peanut;
      case 'treeNuts':
        return treeNuts;
      case 'almond':
        return almond;
      case 'walnut':
        return walnut;
      case 'cashew':
        return cashew;
      case 'pistachio':
        return pistachio;
      case 'hazelnut':
        return hazelnut;
      case 'macadamia':
        return macadamia;
      case 'brazilNut':
        return brazilNut;
      case 'pecan':
        return pecan;
      case 'coconut':
        return coconut;
      case 'shea':
        return shea;
      case 'argan':
        return argan;
      case 'kukui':
        return kukui;
      default:
        return false;
    }
  }

  AllergyProfile setValue(String key, bool value) {
    switch (key) {
      case 'peanut':
        return copyWith(peanut: value);
      case 'treeNuts':
        return copyWith(treeNuts: value);
      case 'almond':
        return copyWith(almond: value);
      case 'walnut':
        return copyWith(walnut: value);
      case 'cashew':
        return copyWith(cashew: value);
      case 'pistachio':
        return copyWith(pistachio: value);
      case 'hazelnut':
        return copyWith(hazelnut: value);
      case 'macadamia':
        return copyWith(macadamia: value);
      case 'brazilNut':
        return copyWith(brazilNut: value);
      case 'pecan':
        return copyWith(pecan: value);
      case 'coconut':
        return copyWith(coconut: value);
      case 'shea':
        return copyWith(shea: value);
      case 'argan':
        return copyWith(argan: value);
      case 'kukui':
        return copyWith(kukui: value);
      default:
        return this;
    }
  }

  AllergyProfile copyWith({
    bool? peanut,
    bool? treeNuts,
    bool? almond,
    bool? walnut,
    bool? cashew,
    bool? pistachio,
    bool? hazelnut,
    bool? macadamia,
    bool? brazilNut,
    bool? pecan,
    bool? coconut,
    bool? shea,
    bool? argan,
    bool? kukui,
  }) {
    return AllergyProfile(
      peanut: peanut ?? this.peanut,
      treeNuts: treeNuts ?? this.treeNuts,
      almond: almond ?? this.almond,
      walnut: walnut ?? this.walnut,
      cashew: cashew ?? this.cashew,
      pistachio: pistachio ?? this.pistachio,
      hazelnut: hazelnut ?? this.hazelnut,
      macadamia: macadamia ?? this.macadamia,
      brazilNut: brazilNut ?? this.brazilNut,
      pecan: pecan ?? this.pecan,
      coconut: coconut ?? this.coconut,
      shea: shea ?? this.shea,
      argan: argan ?? this.argan,
      kukui: kukui ?? this.kukui,
    );
  }

  Map<String, dynamic>? toRequestJson() {
    if (!hasSelections) {
      return null;
    }
    return {
      'peanut': peanut,
      'tree_nuts': treeNuts,
      'almond': almond,
      'walnut': walnut,
      'cashew': cashew,
      'pistachio': pistachio,
      'hazelnut': hazelnut,
      'macadamia': macadamia,
      'brazil_nut': brazilNut,
      'pecan': pecan,
      'coconut': coconut,
      'shea': shea,
      'argan': argan,
      'kukui': kukui,
    };
  }

  Map<String, bool> toStorageJson() {
    return {
      'peanut': peanut,
      'treeNuts': treeNuts,
      'almond': almond,
      'walnut': walnut,
      'cashew': cashew,
      'pistachio': pistachio,
      'hazelnut': hazelnut,
      'macadamia': macadamia,
      'brazilNut': brazilNut,
      'pecan': pecan,
      'coconut': coconut,
      'shea': shea,
      'argan': argan,
      'kukui': kukui,
    };
  }

  factory AllergyProfile.fromJson(Map<String, dynamic> json) {
    bool boolValue(String key, [String? legacyKey]) {
      final value = json[key] ?? (legacyKey == null ? null : json[legacyKey]);
      return value is bool ? value : false;
    }

    return AllergyProfile(
      peanut: boolValue('peanut'),
      treeNuts: boolValue('treeNuts', 'tree_nuts'),
      almond: boolValue('almond'),
      walnut: boolValue('walnut'),
      cashew: boolValue('cashew'),
      pistachio: boolValue('pistachio'),
      hazelnut: boolValue('hazelnut'),
      macadamia: boolValue('macadamia'),
      brazilNut: boolValue('brazilNut', 'brazil_nut'),
      pecan: boolValue('pecan'),
      coconut: boolValue('coconut'),
      shea: boolValue('shea'),
      argan: boolValue('argan'),
      kukui: boolValue('kukui'),
    );
  }
}

class AllergyProfileField {
  const AllergyProfileField({
    required this.key,
    required this.label,
  });

  final String key;
  final String label;
}
