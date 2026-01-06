# .midoriai Folder Usage Audit

**Audit Date:** January 6, 2025  
**Auditor:** Auditor Mode  
**Project:** Stained Glass Odyssey Idle  
**Audit Scope:** Complete codebase review of `.midoriai` folder usage and data storage patterns

---

## Executive Summary

The `.midoriai` folder is currently used as a unified data storage location for user settings and save files in the Stained Glass Odyssey Idle game. This audit identifies all references, documents the current structure, and proposes a game-specific subfolder structure to support future multi-game scenarios.

**Key Findings:**
- 2 files reference `.midoriai`: `settings.py` and `save.py`
- 2 types of data stored: user settings and game save files
- Currently no namespace isolation between potential multiple games
- Folder created on-demand (does not exist until first save)

---

## 1. Current References to `.midoriai`

### 1.1 Code References

All references found via comprehensive grep search:

| File | Line | Purpose | Path Used |
|------|------|---------|-----------|
| `endless_idler/settings.py` | 35-36 | Settings file path | `~/.midoriai/settings.json` |
| `endless_idler/save.py` | 182 | Game save file path | `~/.midoriai/idlesave.json` |

**Search Command Used:**
```bash
grep -rn "\.midoriai" /home/midori-ai/workspace
```

**Result:** Only 3 line references found across 2 files.

### 1.2 File Details

#### `endless_idler/settings.py`
```python
def _default_settings_path() -> Path:
    """Default settings path: ~/.midoriai/settings.json"""
    return Path.home() / ".midoriai" / "settings.json"
```

**Usage Context:**
- Used by `SettingsManager` class
- Stores user preferences (tutorial state, UI settings, audio, accessibility)
- Creates parent directory automatically on save (line 73: `mkdir(parents=True, exist_ok=True)`)
- Falls back gracefully if file doesn't exist or is corrupted

#### `endless_idler/save.py`
```python
def _default_save_path() -> Path:
    override = os.environ.get("ENDLESS_IDLER_SAVE_PATH", "").strip()
    if override:
        return Path(override).expanduser()
    
    home = Path.home()
    if home.exists():
        return home / ".midoriai" / "idlesave.json"
    
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not base:
        base = str(Path.cwd())
    return Path(base) / "idlesave.json"
```

**Usage Context:**
- Used by `SaveManager` class
- Stores complete game state (RunSave dataclass)
- Supports environment variable override: `ENDLESS_IDLER_SAVE_PATH`
- Falls back to Qt's standard location or current directory if home doesn't exist
- Creates parent directory automatically on save (line 169: `mkdir(parents=True, exist_ok=True)`)

---

## 2. Data Being Saved

### 2.1 Settings Data (`settings.json`)

**File:** `~/.midoriai/settings.json`  
**Format:** JSON with 2-space indentation  
**Size:** Small (~300 bytes typical)  
**Write Strategy:** Atomic write via temporary file

**Data Structure:**
```json
{
  "tutorial_completed": false,
  "tutorial_skipped": false,
  "first_launch": true,
  "show_tooltips": true,
  "tooltip_delay_ms": 500,
  "audio_enabled": true,
  "audio_volume": 0.8,
  "music_volume": 0.6,
  "sfx_volume": 0.8,
  "reduced_motion": false,
  "high_contrast": false
}
```

**Purpose:** User preferences and UI settings that persist across runs

### 2.2 Game Save Data (`idlesave.json`)

**File:** `~/.midoriai/idlesave.json`  
**Format:** JSON with 2-space indentation, sorted keys  
**Size:** Variable (grows with character roster, ~5-50KB typical)  
**Write Strategy:** Atomic write via temporary file  
**Version:** Currently at SAVE_VERSION = 8

**Data Structure (Key Fields):**
```json
{
  "version": 8,
  "tokens": 20,
  "party_level": 1,
  "party_level_up_cost": 4,
  "fight_number": 1,
  "party_hp_max": 100,
  "party_hp_current": 100,
  "party_hp_last_idle_heal_at": 0.0,
  "bar": [null, null, null, null, null, null],
  "onsite": [null, null, null, null],
  "offsite": [null, null, null, null, null, null],
  "standby": [null, null, null, null, null, null, null, null, null, null],
  "stacks": {},
  "character_progress": {},
  "character_stats": {},
  "character_initial_stats": {},
  "character_deaths": {},
  "idle_exp_bonus_seconds": 0.0,
  "idle_exp_penalty_seconds": 0.0,
  "idle_shared_exp_percentage": 0,
  "idle_risk_reward_level": 0,
  "winstreak": 0
}
```

**Purpose:** Complete game state including party composition, character progression, combat state, and idle bonuses

**Referenced in Documentation:** `.codex/implementation/save-system.md`

---

## 3. Current Folder Structure

### 3.1 Actual Structure (When Created)

```
~/.midoriai/
├── settings.json       # User preferences (SettingsManager)
└── idlesave.json       # Game save data (SaveManager)
```

### 3.2 Creation Behavior

**Status:** Folder does not exist in current environment
```bash
$ ls -la ~/.midoriai
ls: cannot access '/home/midori-ai/.midoriai': No such file or directory
```

**Creation Trigger:** Created on first save operation by either:
- `SettingsManager.save()` → line 73: `self._path.parent.mkdir(parents=True, exist_ok=True)`
- `SaveManager.save()` → line 169: `self._path.parent.mkdir(parents=True, exist_ok=True)`

**Permissions:** Standard user directory permissions (0755 typical)

---

## 4. Issues Identified

### 4.1 Namespace Collision Risk

**Severity:** Medium  
**Impact:** Future multi-game support

**Issue:** If Midori AI develops multiple games (e.g., "Stained Glass Odyssey Idle", "Stained Glass Arena", "Stained Glass Quest"), all would potentially write to the same `.midoriai/` folder without game-specific namespacing.

**Current Risk:**
- `settings.json` naming conflict between games
- `idlesave.json` naming conflict between games
- No isolation of game-specific data

### 4.2 Lack of Environment Variable for Settings

**Severity:** Low  
**Impact:** Testing and development flexibility

**Issue:** `save.py` provides `ENDLESS_IDLER_SAVE_PATH` override, but `settings.py` has no equivalent environment variable override for testing or alternate configurations.

**Current Behavior:**
- Save path: Configurable via `ENDLESS_IDLER_SAVE_PATH` ✓
- Settings path: Hardcoded to `.midoriai/settings.json` ✗

### 4.3 Inconsistent Fallback Strategies

**Severity:** Low  
**Impact:** Cross-platform consistency

**Issue:** Different fallback approaches between settings and save managers:
- `settings.py`: Fails silently if path doesn't work, returns defaults
- `save.py`: Falls back to Qt's AppDataLocation, then current directory

**Implications:** Save file might end up in different locations than settings file on systems where `Path.home()` fails.

---

## 5. Proposed Folder Structure

### 5.1 Recommended Structure

```
~/.midoriai/                                  # Root data folder for all Midori AI games
├── stained-glass-odyssey/                    # Game-specific subfolder
│   ├── settings.json                         # User preferences for this game
│   ├── saves/                                # Save file directory
│   │   ├── idlesave.json                     # Current run save
│   │   ├── autosave-*.json                   # Future: autosave backups
│   │   └── manual-*.json                     # Future: manual save slots
│   ├── profiles/                             # Future: multiple player profiles
│   │   └── default/
│   │       ├── settings.json
│   │       └── saves/
│   └── cache/                                # Future: cached assets, temp files
│       └── .gitkeep
├── stained-glass-arena/                      # Future game 2
│   └── ...
└── stained-glass-quest/                      # Future game 3
    └── ...
```

### 5.2 Migration Path Structure

**Phase 1: Immediate (Backward Compatible)**
```
~/.midoriai/
├── settings.json                             # Legacy location (deprecated)
├── idlesave.json                             # Legacy location (deprecated)
└── stained-glass-odyssey/                    # New location
    ├── settings.json                         # Primary location
    └── idlesave.json                         # Primary location
```

**Migration Logic:**
1. Check new path first: `~/.midoriai/stained-glass-odyssey/`
2. If not found, check legacy path: `~/.midoriai/`
3. If found in legacy, load and save to new path
4. Keep legacy file for 1-2 versions for safety

**Phase 2: Future (Clean Structure)**
- Remove legacy file support
- Add `saves/` subdirectory for multiple save slots
- Add `profiles/` support for multi-user scenarios

### 5.3 Naming Convention

**Game Folder Names:**
- Use lowercase with hyphens
- Match repository name style
- Examples:
  - `stained-glass-odyssey` (this game)
  - `stained-glass-arena` (future)
  - `stained-glass-quest` (future)

**Why This Convention:**
- Consistent with GitHub repository naming
- Cross-platform compatible (no spaces, lowercase)
- URL-friendly if needed for cloud sync features
- Human-readable and intuitive

---

## 6. Recommendations

### 6.1 Immediate Actions (Priority: High)

1. **Create Game Subfolder Structure**
   - Update `settings.py` to use `~/.midoriai/stained-glass-odyssey/settings.json`
   - Update `save.py` to use `~/.midoriai/stained-glass-odyssey/idlesave.json`
   - Implement backward-compatible migration for existing users
   - Add migration tests

2. **Add Environment Variable Override for Settings**
   - Implement `ENDLESS_IDLER_SETTINGS_PATH` similar to save path override
   - Document in README.md
   - Update tests to use override in CI/CD

3. **Update Documentation**
   - Update `.codex/implementation/save-system.md` with new paths
   - Add migration notes for users with existing saves
   - Document folder structure in README.md

### 6.2 Future Enhancements (Priority: Medium)

4. **Standardize Fallback Logic**
   - Make both managers use consistent fallback approach
   - Consider using Qt's AppDataLocation for both on all platforms
   - Document platform-specific behavior

5. **Add Save Slot Support**
   - Create `saves/` subdirectory structure
   - Implement numbered or named save slots
   - Add UI for save management

6. **Profile Support**
   - Add `profiles/` subdirectory
   - Allow multiple users to play on same machine
   - Each profile has own settings and saves

### 6.3 Testing Requirements

7. **Test Coverage Needed**
   - Migration from legacy paths to new paths
   - Handling of missing/corrupted legacy files during migration
   - Environment variable overrides for both settings and saves
   - Cross-platform path handling (Windows, macOS, Linux)
   - Fallback behavior when home directory unavailable

### 6.4 Code Quality

8. **Consistency Improvements**
   - Extract common path resolution logic to shared utility
   - Consider creating a `PathManager` class for all game data paths
   - Add type hints for all path-related functions
   - Document all path resolution strategies in docstrings

---

## 7. Implementation Checklist

### Phase 1: Game Namespace Migration (Estimated: 2-3 hours)

- [ ] Create `_default_settings_path_v2()` with migration logic
- [ ] Create `_default_save_path_v2()` with migration logic  
- [ ] Add `ENDLESS_IDLER_SETTINGS_PATH` environment variable
- [ ] Update `SettingsManager` to use new path with migration
- [ ] Update `SaveManager` to use new path with migration
- [ ] Add migration helper function `_migrate_legacy_file()`
- [ ] Update `.codex/implementation/save-system.md`
- [ ] Add migration notes to README.md
- [ ] Write unit tests for migration logic
- [ ] Test on clean environment (no existing saves)
- [ ] Test with existing legacy saves
- [ ] Manual test on Linux (current platform)

### Phase 2: Documentation & Cleanup (Estimated: 1 hour)

- [ ] Document new folder structure in code comments
- [ ] Add deprecation warnings for legacy paths (log only)
- [ ] Update all path-related docstrings
- [ ] Add example paths for all platforms to documentation
- [ ] Create `.codex/implementation/data-storage.md` for comprehensive path docs

### Phase 3: Future Preparation (Deferred)

- [ ] Design `saves/` subdirectory API
- [ ] Design `profiles/` subdirectory API
- [ ] Create `PathManager` utility class
- [ ] Add save slot UI mockups
- [ ] Plan cloud sync architecture (if applicable)

---

## 8. Risk Assessment

### 8.1 Migration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data loss during migration | Low | Critical | Atomic writes, backup before migrate |
| User confusion about new paths | Low | Low | Keep backward compatibility, silent migration |
| Platform-specific path issues | Medium | Medium | Extensive cross-platform testing |
| Corrupted legacy files break migration | Low | Medium | Graceful fallback, log errors |

### 8.2 Compatibility Concerns

**Backward Compatibility:** HIGH PRIORITY
- Existing users must not lose saves
- Migration must be transparent
- Fallback to legacy paths if new path fails

**Forward Compatibility:** MEDIUM PRIORITY
- New structure should support future features
- Consider versioning in folder structure if needed
- Design extensible enough for multi-game scenario

---

## 9. Related Files for Review

When implementing changes, review and potentially update:

1. **Code Files:**
   - `endless_idler/settings.py` - Primary change location
   - `endless_idler/save.py` - Primary change location
   - `endless_idler/save_codec.py` - May need updates for migration
   - `endless_idler/app.py` - May reference these paths
   - `main.py` - Entry point, may need path setup

2. **Documentation Files:**
   - `.codex/implementation/save-system.md` - Must update
   - `README.md` - Add data storage section
   - `.codex/implementation/AGENTS.md` - Check for references

3. **Test Files:**
   - Create `tests/test_migration.py` for migration logic
   - Update any existing tests that mock file paths
   - Add integration tests for path resolution

---

## 10. Platform Considerations

### 10.1 Linux (Current Platform)

**Default Path:** `~/.midoriai/stained-glass-odyssey/`  
**Resolved:** `/home/midori-ai/.midoriai/stained-glass-odyssey/`  
**Status:** ✓ Standard hidden folder convention

### 10.2 Windows

**Default Path:** `%USERPROFILE%\.midoriai\stained-glass-odyssey\`  
**Resolved:** `C:\Users\{username}\.midoriai\stained-glass-odyssey\`  
**Alternative:** Qt AppDataLocation: `%APPDATA%\Stained-Glass-Odyssey-Idle\`  
**Considerations:**
- Windows prefers visible folders in AppData
- Hidden folders (dot prefix) are less common but supported
- Consider using Qt's location as primary on Windows

### 10.3 macOS

**Default Path:** `~/.midoriai/stained-glass-odyssey/`  
**Resolved:** `/Users/{username}/.midoriai/stained-glass-odyssey/`  
**Alternative:** `~/Library/Application Support/Stained-Glass-Odyssey-Idle/`  
**Considerations:**
- macOS standard is Application Support folder
- Hidden folders work but less discoverable
- Consider platform-specific paths

### 10.4 Recommendation

**Option A (Current Approach):** Dot folder for all platforms
- ✓ Consistent across platforms
- ✓ Simple implementation
- ✗ Less discoverable on Windows/macOS

**Option B (Platform-Specific):** Use Qt's AppDataLocation
- ✓ Platform-native conventions
- ✓ More discoverable
- ✗ Different paths per platform
- ✗ Existing code already has fallback to this

**Recommended:** Keep Option A (dot folder) as primary, Option B as fallback (already implemented in save.py)

---

## 11. Code Examples

### 11.1 Proposed Settings Path Function

```python
def _default_settings_path() -> Path:
    """Default settings path with game namespace.
    
    Returns:
        Path to settings.json in game-specific subfolder.
        
    Priority:
        1. Environment variable: ENDLESS_IDLER_SETTINGS_PATH
        2. Game subfolder: ~/.midoriai/stained-glass-odyssey/settings.json
        3. Legacy location: ~/.midoriai/settings.json (for migration)
    """
    # Check environment override first
    override = os.environ.get("ENDLESS_IDLER_SETTINGS_PATH", "").strip()
    if override:
        return Path(override).expanduser()
    
    # New game-specific location
    return Path.home() / ".midoriai" / "stained-glass-odyssey" / "settings.json"


def _legacy_settings_path() -> Path:
    """Legacy settings path for backward compatibility."""
    return Path.home() / ".midoriai" / "settings.json"


def _migrate_settings_if_needed(new_path: Path, legacy_path: Path) -> None:
    """Migrate settings from legacy location to new location.
    
    Args:
        new_path: Target path in game-specific subfolder
        legacy_path: Old path in root .midoriai folder
    """
    # Skip if new path already exists
    if new_path.exists():
        return
    
    # Skip if legacy path doesn't exist
    if not legacy_path.exists():
        return
    
    try:
        # Ensure new directory exists
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy legacy file to new location
        import shutil
        shutil.copy2(legacy_path, new_path)
        
        # Optionally: Keep legacy file for safety (can be removed in future version)
        # legacy_path.unlink()
        
    except (OSError, IOError) as e:
        # Migration failed, but don't crash - new path will use defaults
        import logging
        logging.warning(f"Failed to migrate settings from {legacy_path} to {new_path}: {e}")
```

### 11.2 Proposed Save Path Function

```python
def _default_save_path() -> Path:
    """Default save path with game namespace.
    
    Returns:
        Path to idlesave.json in game-specific subfolder.
        
    Priority:
        1. Environment variable: ENDLESS_IDLER_SAVE_PATH
        2. Game subfolder: ~/.midoriai/stained-glass-odyssey/idlesave.json
        3. Legacy location: ~/.midoriai/idlesave.json (for migration)
        4. Qt AppDataLocation fallback
        5. Current directory fallback
    """
    # Check environment override first
    override = os.environ.get("ENDLESS_IDLER_SAVE_PATH", "").strip()
    if override:
        return Path(override).expanduser()
    
    # Try home directory with game namespace
    home = Path.home()
    if home.exists():
        return home / ".midoriai" / "stained-glass-odyssey" / "idlesave.json"
    
    # Fallback to Qt's standard location
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not base:
        base = str(Path.cwd())
    return Path(base) / "idlesave.json"


def _legacy_save_path() -> Path:
    """Legacy save path for backward compatibility."""
    home = Path.home()
    if home.exists():
        return home / ".midoriai" / "idlesave.json"
    return Path("")  # Invalid path if home doesn't exist
```

---

## 12. Success Metrics

After implementation, verify:

1. **Functional:**
   - [ ] New installs use game-specific folder
   - [ ] Existing saves migrate automatically
   - [ ] No data loss during migration
   - [ ] Environment overrides work for both settings and saves

2. **Code Quality:**
   - [ ] No code duplication in path resolution
   - [ ] Comprehensive error handling
   - [ ] All paths documented
   - [ ] Test coverage >80% for migration logic

3. **User Experience:**
   - [ ] Migration is invisible to users
   - [ ] No manual intervention required
   - [ ] Clear documentation if users need to find files
   - [ ] Support article for manual migration if needed

---

## 13. Conclusion

The current `.midoriai` folder implementation is functional but lacks namespace isolation for future multi-game scenarios. The proposed migration to `~/.midoriai/stained-glass-odyssey/` provides:

1. **Future-proofing:** Clear separation for multiple games
2. **Backward compatibility:** Automatic migration from legacy paths
3. **Consistency:** Environment variable support for both settings and saves
4. **Extensibility:** Structure supports save slots and profiles

**Recommendation:** Proceed with Phase 1 implementation (game namespace migration) before adding significant new features that depend on data storage. This prevents technical debt and simplifies future enhancements.

**Estimated Total Effort:** 3-4 hours for complete Phase 1 + Phase 2

**Next Steps:**
1. Review this audit with team
2. Approve recommended structure
3. Create implementation task in `.codex/tasks/wip/`
4. Assign to Coder mode for implementation
5. Submit for Reviewer mode validation
6. Final Auditor review before merge

---

**Audit Completed:** January 6, 2025  
**Report Version:** 1.0  
**Status:** Ready for team review
