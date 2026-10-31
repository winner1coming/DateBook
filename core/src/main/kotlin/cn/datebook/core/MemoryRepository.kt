package cn.datebook.core

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.time.Clock

/** 测试和离线业务验证用仓库；生产由 RoomStore 实现同一契约。 */
class MemoryRepository(seed: LibraryState = defaultLibrary(), private val clock: Clock = Clock.systemUTC()) : LibraryRepository {
 private val mutex = Mutex()
 private val current = MutableStateFlow(seed)
 private val receipts = LinkedHashMap<String, Any?>()
 override val state: StateFlow<LibraryState> = current.asStateFlow()
 init { LibraryValidator.validate(seed) }
 @Suppress("UNCHECKED_CAST")
 override suspend fun <T> transaction(operationId: String, expectedEpoch: String?, block: (LibraryState) -> Change<T>): T = mutex.withLock {
  val old = current.value
  demand(expectedEpoch == null || expectedEpoch == old.epoch, "LIBRARY_STALE")
  demand(operationId.isNotBlank() && operationId.length <= 128, "INPUT_INVALID", "operationId")
  if (receipts.containsKey(operationId)) return@withLock receipts[operationId] as T
  val change = block(old)
  demand(change.state.id == old.id && change.state.epoch == old.epoch && change.state.revision == old.revision, "LIBRARY_IDENTITY_INVALID")
  LibraryValidator.validate(change.state)
  if (change.state != old) current.value = change.state.copy(revision = old.revision + 1, updatedAt = clock.millis())
  receipts[operationId] = change.result
  change.result
 }
 override suspend fun install(candidate: LibraryState, expectedRevision: Long, expectedEpoch: String): LibraryState = mutex.withLock {
  val old = current.value
  demand(old.epoch == expectedEpoch && old.revision == expectedRevision, "PREVIEW_STALE")
  LibraryValidator.validate(candidate)
  val installed = candidate.copy(epoch = newId(), revision = old.revision + 1, updatedAt = clock.millis())
  current.value = installed
  receipts.clear()
  installed
 }
}
