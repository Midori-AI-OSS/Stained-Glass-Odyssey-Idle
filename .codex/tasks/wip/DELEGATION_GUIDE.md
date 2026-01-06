# Passive System Implementation - Quick Delegation Guide

**Master Task**: 7437c51e-passive-system-overview  
**Created**: 2024-01-06  
**Total Tasks**: 6 (+ 1 overview)

## How to Use This Guide

Each task can be delegated to the appropriate sub-agent using the task tool. Tasks are numbered in execution order, but some can run in parallel.

## Task Execution Order

### Phase 1: Foundation (Parallel)
These can be started simultaneously:

**Task 1e4e2d6b** - Base Infrastructure  
**Task b243ccf7** - Metadata Extraction

### Phase 2: Passive Implementations (Parallel)
Start after Phase 1 completes:

**Task 04f7b1f9** - Lady Light Radiant Aegis  
**Task 91a0af9d** - Lady Darkness Eclipsing Veil  
**Task cea883a7** - Trinity Synergy

### Phase 3: Integration (Sequential)
Start after all passive implementations complete:

**Task 1f19c441** - Combat Integration

## Delegation Commands

### Start Phase 1

```
Delegate to coder: Implement task 1e4e2d6b-passive-base-infrastructure
```

```
Delegate to coder: Implement task b243ccf7-metadata-passive-extraction
```

### Start Phase 2 (after Phase 1)

```
Delegate to coder: Implement task 04f7b1f9-lady-light-radiant-aegis
```

```
Delegate to coder: Implement task 91a0af9d-lady-darkness-eclipsing-veil
```

```
Delegate to coder: Implement task cea883a7-trinity-synergy-passive
```

### Start Phase 3 (after Phase 2)

```
Delegate to coder: Implement task 1f19c441-combat-passive-integration
```

### Auditing (after each task)

After each coder completes a task and moves it to `.codex/tasks/review/`:

```
Delegate to auditor: Review task [TASK_ID] in review folder
```

## Task Summary Table

| ID | Name | Complexity | Dependencies | Est. Time |
|----|------|------------|--------------|-----------|
| 1e4e2d6b | Base Infrastructure | Medium | None | 2-3 hours |
| b243ccf7 | Metadata Extraction | Low | None | 1-2 hours |
| 04f7b1f9 | Lady Light Passive | Medium | 1e4e2d6b, b243ccf7 | 2-3 hours |
| 91a0af9d | Lady Darkness Passive | Medium | 1e4e2d6b, b243ccf7 | 2-3 hours |
| cea883a7 | Trinity Synergy | High | 1e4e2d6b, b243ccf7 | 4-5 hours |
| 1f19c441 | Combat Integration | High | All above | 4-6 hours |

**Total Estimated Time**: 15-22 hours

## Progress Tracking

Use this checklist to track completion:

### Phase 1: Foundation
- [ ] Task 1e4e2d6b - Base Infrastructure
  - [ ] Coder implementation complete
  - [ ] Moved to review folder
  - [ ] Auditor review complete
  - [ ] Moved to taskmaster folder
  
- [ ] Task b243ccf7 - Metadata Extraction
  - [ ] Coder implementation complete
  - [ ] Moved to review folder
  - [ ] Auditor review complete
  - [ ] Moved to taskmaster folder

### Phase 2: Passive Implementations
- [ ] Task 04f7b1f9 - Lady Light Passive
  - [ ] Coder implementation complete
  - [ ] Moved to review folder
  - [ ] Auditor review complete
  - [ ] Moved to taskmaster folder

- [ ] Task 91a0af9d - Lady Darkness Passive
  - [ ] Coder implementation complete
  - [ ] Moved to review folder
  - [ ] Auditor review complete
  - [ ] Moved to taskmaster folder

- [ ] Task cea883a7 - Trinity Synergy
  - [ ] Coder implementation complete
  - [ ] Moved to review folder
  - [ ] Auditor review complete
  - [ ] Moved to taskmaster folder

### Phase 3: Integration
- [ ] Task 1f19c441 - Combat Integration
  - [ ] Coder implementation complete
  - [ ] Moved to review folder
  - [ ] Auditor review complete
  - [ ] Moved to taskmaster folder

### Final Steps
- [ ] All tasks approved by taskmaster
- [ ] Integration testing complete
- [ ] Documentation updated
- [ ] Commit and PR created

## Agent Roles

### Coder Agent
- Implements code according to task specifications
- Writes tests and documentation
- Runs linting before committing
- Moves completed tasks from `wip/` to `review/`

### Auditor Agent
- Reviews code quality and correctness
- Verifies all acceptance criteria met
- Checks for edge cases and potential issues
- Moves approved tasks to `taskmaster/` or back to `wip/` with feedback

### Taskmaster (You)
- Final review and approval
- Closes completed tasks
- Manages dependencies and blocking issues
- Coordinates between agents

## Common Issues & Solutions

### Issue: Task blocked on dependency
**Solution**: Ensure dependency task is fully complete and in `taskmaster/` before starting

### Issue: Coder encounters unclear requirements
**Solution**: Coder should add questions to task file, taskmaster clarifies

### Issue: Auditor finds issues
**Solution**: Move task back to `wip/` with detailed feedback in task file

### Issue: Integration task reveals problems in earlier tasks
**Solution**: Create new tasks or reopen earlier tasks to fix issues

## Files by Phase

### Phase 1 Creates
- `endless_idler/passives/__init__.py`
- `endless_idler/passives/base.py`
- `endless_idler/passives/triggers.py`
- `endless_idler/passives/registry.py`
- `endless_idler/passives/implementations/__init__.py`
- Updated: `endless_idler/characters/metadata.py`

### Phase 2 Creates
- `endless_idler/passives/implementations/lady_light_radiant_aegis.py`
- `endless_idler/passives/implementations/lady_darkness_eclipsing_veil.py`
- `endless_idler/passives/implementations/trinity_synergy.py`
- Updated: Character files to add `trinity_synergy` passive

### Phase 3 Modifies
- `endless_idler/combat/stats.py` (add fields)
- Character loading code (load passives)
- Combat turn execution (add triggers)
- Damage calculation (integrate PRE_DAMAGE)
- Target selection (integrate TARGET_SELECTION)
- New: `.codex/implementation/passive-system.md` (documentation)

## Success Metrics

- [ ] All passive IDs extracted from character metadata
- [ ] All three passives implemented and registered
- [ ] Passives trigger during combat
- [ ] Lady Light heals party when offsite
- [ ] Lady Darkness deals enhanced damage
- [ ] Trinity synergy activates with all three present
- [ ] No breaking changes to existing code
- [ ] All tests pass
- [ ] Code passes linting

## Next Steps After Completion

1. Test in actual gameplay
2. Balance passive effects if needed
3. Add more passives for other characters
4. Create UI to show active passives
5. Add passive descriptions to character sheets
