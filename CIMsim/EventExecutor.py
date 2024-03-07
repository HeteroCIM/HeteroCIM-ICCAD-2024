from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.Event import *
from CIMsim.Tile import *
from CIMsim.Buffer import *
def executeEvent(event):
    if event.event_type == EventType.LoadEvent:
        assert isinstance(event.src, DRAM), "src of load event must be DRAM"
        src_read_T, src_read_E = event.src.read(event.data_size)
        dst_write_T, dst_write_E = event.dst.write(event.data_size)
        event_T = max(src_read_T, dst_write_T)
        event_E = src_read_E + dst_write_E
        return event_T, event_E
    elif event.event_type == EventType.StoreEvent:
        assert isinstance(event.dst, DRAM), "dst of store event must be DRAM"
        src_read_T, src_read_E = event.src.read(event.data_size)
        dst_write_T, dst_write_E = event.dst.write(event.data_size)
        event_T = max(src_read_T, dst_write_T)
        event_E = src_read_E + dst_write_E
        return event_T, event_E
    elif event.event_type == EventType.MoveEvent:
        if isinstance(event.src, Buffer) and isinstance(event.dst, Buffer):
            # data transmission between buffer and buffer
            assert 0, "why it happens?"
        elif isinstance(event.src, Buffer) and isinstance(event.dst, Tile):
            # data transmission from global buffer to tile
            src_read_T, src_read_E = event.src.read(event.data_size)
            dst_write_T, dst_write_E = event.dst.input_reg.write(event.data_size)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E
        elif isinstance(event.src, Tile) and isinstance(event.dst, Tile):
            # data transmission between tile and tile
            src_read_T, src_read_E = event.src.output_reg.read(event.data_size)
            dst_write_T, dst_write_E = event.dst.input_reg.write(event.data_size)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E
        elif isinstance(event.src, Tile) and isinstance(event.dst, Buffer):
            # data transmission from tile to global buffer
            src_read_T, src_read_E = event.src.output_reg.read(event.data_size)
            dst_write_T, dst_write_E = event.dst.write(event.data_size)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E
        return event_T, event_E
    elif event.event_type == EventType.MatmulEvent:
        assert isinstance(event.assigned_hardware, Tile), "matmul must be calculated in tile!"
        assert event.input1_shape[1] == event.input2_shape[0], "matrix dimensions don't match!"
        event_T = 0
        event_E = 0
        assert (event.input2_shape[0] <= event.assigned_hardware.crossbar.n_rows) and (event.input2_shape[1] <= event.assigned_hardware.crossbar.n_cols), "weight partition not implemented yet"
        for i in range(event.input1_shape[0]):
            cal_T, cal_E = event.assigned_hardware.compute(event.input1_shape[1], event.input2_shape[1]) 
            event_T += cal_T
            event_E += cal_E
        return event_T, event_E