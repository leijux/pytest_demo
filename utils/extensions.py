import jsonschema
import json

from syrupy.types import SerializableData, SerializedData
from syrupy.data import SnapshotCollection, Snapshot
from utils.schema import generate_json_schema
from utils._utils import json_dumps

from syrupy.terminal import (
    reset,
    received_style,
    snapshot_style,
    context_style,
    received_diff_style,
    snapshot_diff_style,
)
from syrupy.constants import (
    DISABLE_COLOR_ENV_VAR,
    SNAPSHOT_DIRNAME,
    SYMBOL_CARRIAGE,
    SYMBOL_ELLIPSIS,
    SYMBOL_NEW_LINE,
)

from typing import (
    TYPE_CHECKING,
    Any,
    Optional, Iterator,
)

from syrupy.constants import SYMBOL_ELLIPSIS
from syrupy.extensions.single_file import (
    SingleFileSnapshotExtension,
    WriteMode,
)

if TYPE_CHECKING:
    from syrupy.types import (
        SerializableData,
        SerializedData,
    )


class JSONSchemaSnapshotExtension(SingleFileSnapshotExtension):
    _write_mode = WriteMode.TEXT
    _file_extension = "json"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.validation_error: Optional[jsonschema.ValidationError] = None

    def serialize(self, data: "SerializableData", **kwargs: Any) -> "SerializedData":
        if isinstance(data, str):
            return data
        return json_dumps(data)

    def matches(
            self,
            *,
            serialized_data: SerializableData,
            snapshot_data: SerializableData,
            **kwargs: Any
    ) -> bool:
        try:
            schema = json.loads(snapshot_data)
            jsonschema.validate(instance=json.loads(serialized_data), schema=schema)
            return True
        except jsonschema.ValidationError as e:
            self.validation_error = e
            return False
        except json.JSONDecodeError as e:
            self.validation_error = Exception(f"Invalid stored schema: {str(e)}")
            return False

    def diff_lines(
            self,
            serialized_data: SerializedData,
            snapshot_data: SerializedData
    ) -> Iterator[str]:
        """生成结构化错误报告"""
        if not self.validation_error:
            yield from super().diff_lines(serialized_data, snapshot_data)
            return

        # 提取错误详情
        error = self.validation_error
        error_path = ".".join(map(str, error.absolute_path))
        schema_path = ".".join(map(str, error.schema_path))

        # 构建对比输出
        yield received_style("Data Validation Error:")
        yield ""
        yield f"{context_style('Error Path:')} {received_style(error_path)}"
        yield f"{context_style('Schema Path:')} {snapshot_style(schema_path)}"
        yield ""
        yield received_style("Error Message:")
        yield f"  {received_diff_style(str(error.message))}"
        yield ""

        # 显示Schema要求与实际数据对比
        if hasattr(error, "schema"):
            yield snapshot_style("Schema Requirements:")
            yield self._format_schema_section(error.schema)

        if error.instance:
            yield received_style("Actual Data:")
            yield self._format_data_section(error.instance)

    def _format_schema_section(self, schema: dict) -> str:
        """格式化Schema片段"""
        schema_str = json.dumps(schema, indent=2)
        return "\n".join(
            f"  {snapshot_style(line)}"
            for line in schema_str.splitlines()[:self._context_line_count + 2]
        ) + f"\n  {context_style(SYMBOL_ELLIPSIS)}"

    def _format_data_section(self, data: Any) -> str:
        """格式化数据片段"""
        data_str = json.dumps(data, indent=2)
        return "\n".join(
            f"  {received_style(line)}"
            for line in data_str.splitlines()[:self._context_line_count + 2]
        ) + f"\n  {context_style(SYMBOL_ELLIPSIS)}"

    @classmethod
    def _write_snapshot_collection(
            cls, *, snapshot_collection: "SnapshotCollection"
    ) -> None:
        snapshot = next(iter(snapshot_collection))
        if str(snapshot) is not None:
            snapshot_collection.add(
                Snapshot(name=snapshot.name, data=generate_json_schema(json.loads(snapshot.data))))

        super()._write_snapshot_collection(snapshot_collection=snapshot_collection)
