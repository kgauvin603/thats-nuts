import 'package:flutter/material.dart';

import '../models/allergy_profile.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({
    super.key,
    required this.initialProfile,
    required this.onProfileSaved,
  });

  static const routeName = '/profile';

  final AllergyProfile initialProfile;
  final ValueChanged<AllergyProfile> onProfileSaved;

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late AllergyProfile _draftProfile;

  @override
  void initState() {
    super.initState();
    _draftProfile = widget.initialProfile;
  }

  void _setField(String key, bool value) {
    setState(() {
      _draftProfile = _draftProfile.setValue(key, value);
    });
  }

  void _clearProfile() {
    setState(() {
      _draftProfile = const AllergyProfile();
    });
  }

  void _saveProfile() {
    widget.onProfileSaved(_draftProfile);
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Allergy Profile'),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 20, 20, 12),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Choose the nut-related ingredients you want the app to focus on.',
                      style: theme.textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _draftProfile.hasSelections
                          ? 'Active profile: ${_draftProfile.summary}'
                          : 'No profile selected. The backend will check across all supported nut-related ingredients.',
                      style: theme.textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              children: [
                for (final field in AllergyProfile.fields)
                  Card(
                    margin: const EdgeInsets.only(bottom: 10),
                    child: SwitchListTile(
                      title: Text(field.label),
                      secondary: const Icon(Icons.eco_rounded),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 4,
                      ),
                      value: _draftProfile.valueFor(field.key),
                      onChanged: (value) => _setField(field.key, value),
                    ),
                  ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _clearProfile,
                    child: const Text('Clear'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton(
                    onPressed: _saveProfile,
                    child: const Text('Apply Profile'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
