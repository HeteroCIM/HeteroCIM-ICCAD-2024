from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.Event import *
from CIMsim.PE import *
from CIMsim.Buffer import *
from CIMsim.NonlinearVecModule import *
def executeEvent(event):
    global_stats = {}
    if event.event_type == EventType.LoadEvent:
        assert isinstance(event.src, DRAM), "src of load event must be DRAM"
        if isinstance(event.dst, Buffer):
            src_read_T, src_read_E = event.src.read(data_size = event.data_size, stats = global_stats)
            dst_write_T, dst_write_E = event.dst.write(data_size = event.data_size, stats = global_stats)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E, global_stats
        elif isinstance(event.dst, PE):
            src_read_T, src_read_E = event.src.read(data_size = event.data_size, stats = global_stats)
            dst_write_T, dst_write_E = event.dst.input_buf.write(data_size = event.data_size, stats = global_stats)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E, global_stats
        else: assert 0
    elif event.event_type == EventType.StoreEvent:
        assert isinstance(event.dst, DRAM), "dst of store event must be DRAM"
        src_read_T, src_read_E = 0, 0
        if isinstance(event.src, Buffer):
            src_read_T, src_read_E = event.src.read(event.data_size, stats = global_stats)
        elif isinstance(event.src, PE):
            src_read_T, src_read_E = event.src.output_buf.read(event.data_size, stats = global_stats)
        dst_write_T, dst_write_E = event.dst.write(event.data_size, stats = global_stats)
        event_T = max(src_read_T, dst_write_T)
        event_E = src_read_E + dst_write_E
        return event_T, event_E, global_stats
    elif event.event_type == EventType.WriteEvent:
        assert isinstance(event.PE, PE), "write event must be executed in a PE"
        event_T, event_E = event.PE.update(event.n_rows, event.n_cols, stats = global_stats)
        return event_T, event_E, global_stats

    elif event.event_type == EventType.MoveEvent:
        if isinstance(event.src, Buffer) and isinstance(event.dst, Buffer):
            # data transmission between buffer and buffer
            assert 0, "why it happens?"
        elif isinstance(event.src, Buffer) and isinstance(event.dst, PE):
            # data transmission from global buffer to PE
            src_read_T, src_read_E = event.src.read(event.data_size, stats = global_stats)
            dst_write_T, dst_write_E = event.dst.input_buf.write(event.data_size, stats = global_stats)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E, global_stats
        elif isinstance(event.src, PE) and isinstance(event.dst, PE):
            # data transmission between PE and PE
            src_read_T, src_read_E = event.src.output_buf.read(event.data_size, stats = global_stats)
            dst_write_T, dst_write_E = event.dst.input_buf.write(event.data_size, stats = global_stats)
            # # need to check
            # bus_T = event.data_size / event.dst.inter_PE_bandwidth
            event_T = max(src_read_T, dst_write_T) #, bus_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E, global_stats
        elif isinstance(event.src, PE) and isinstance(event.dst, Buffer):
            # data transmission from PE to global buffer
            src_read_T, src_read_E = event.src.output_buf.read(event.data_size, stats = global_stats)
            dst_write_T, dst_write_E = event.dst.write(event.data_size, stats = global_stats)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E, global_stats
        elif isinstance(event.src, PE) and isinstance(event.dst, NonlinearVecModule):
            # data transmission between PE and PE
            src_read_T, src_read_E = event.src.output_buf.read(event.data_size, stats = global_stats)
            dst_write_T, dst_write_E = event.dst.nvm_buf.write(event.data_size, stats = global_stats)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E, global_stats
        elif isinstance(event.src, NonlinearVecModule) and isinstance(event.dst, PE):
            # data transmission between PE and PE
            src_read_T, src_read_E = event.src.nvm_buf.read(event.data_size, stats = global_stats)
            dst_write_T, dst_write_E = event.dst.input_buf.write(event.data_size, stats = global_stats)
            event_T = max(src_read_T, dst_write_T)
            event_E = src_read_E + dst_write_E
            return event_T, event_E, global_stats
    elif event.event_type == EventType.VecMatMulEvent:
        assert isinstance(event.hardware, PE), "matmul must be calculated in PE!"
        assert event.input_1_shape[1] == event.input_2_shape[0], "matrix dimensions don't match!"
        event_T = 0
        event_E = 0
        assert (event.input_2_shape[0] <= event.hardware.crossbar.n_rows) and (event.input_2_shape[1] <= event.hardware.crossbar.n_cols), "weight partition not implemented yet"
        if event.input_1_shape[0] != 1:
            print("input is not a vector. Input matrix is divided into vectors")
        for i in range(event.input_1_shape[0]):
            cal_T, cal_E = event.hardware.compute(vector_size = event.input_1_shape[1], active_cols = event.input_2_shape[1], stats = global_stats) 
            event_T += cal_T * event.input_1_shape[0]
            event_E += cal_E * event.input_1_shape[0]
        return event_T, event_E, global_stats
    elif event.event_type == EventType.ActivationEvent:
        event_T, event_E = event.hardware.compute("activation", event.activation_name, input_shape = event.input_shape, stats = global_stats) 
        return event_T, event_E, global_stats
    elif event.event_type == EventType.VectorEvent:
        pass