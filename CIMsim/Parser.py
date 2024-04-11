import os
import json
from CIMsim.DRAM import *
from CIMsim.Crossbar import *
from CIMsim.Event import *
from CIMsim.Tile import *
from CIMsim.Buffer import *
from CIMsim.EventExecutor import *
from CIMsim.NonlinearVecModule import *
from CIMsim.FPGA import *

class Parser():
    def __init__(self, tile_config_path = "", DRAM_config_path = "", FPGA_config_path = "") -> None:
        self.hardware_dict = {} # dict: "tile_name" : Tile
        self.tile_config_path = tile_config_path
        self.DRAM_config_path = DRAM_config_path
        self.FPGA_config_path = FPGA_config_path
        self.tile_NVM_config_path = ""
        self.fpga_name = "FPGA"
        self.opcode_to_vector_dict = {
            "VectorAdd": VectorEventType.VectorAdd,
            "VectorSub": VectorEventType.VectorSub,
            "VectorAdd": VectorEventType.VectorAdd,
            "VectorMul": VectorEventType.VectorMul,
            "VectorDiv": VectorEventType.VectorDiv,
            "VectorMax": VectorEventType.VectorMax,
            "VectorMin": VectorEventType.VectorMin,
            "VectorExp": VectorEventType.VectorExp,
            "VectorSqrt": VectorEventType.VectorSqrt,
            "VectorReLUPWL": VectorEventType.VectorReLU,
            "VectorPReluPWL": VectorEventType.VectorPReLU,
            "VectorGeluPWL": VectorEventType.VectorGeLU,
            "VectorSigmoidPWL": VectorEventType.VectorSigmoid,
            "VectorTanhPWL": VectorEventType.VectorTanh,
            "VectorELUPWL": VectorEventType.VectorELU,
            "VectorSiLUPWL": VectorEventType.VectorSiLU
        }
        self.opcode_to_reduce_dict = {
            "SimpleReduceSoftmax": ReduceEventType.Softmax,
            "SimpleReduceLayernorm": ReduceEventType.Layernorm
        }
    def parse_linecode_file(self, file_path):
        event_list = []
        file = open(file_path,  "r")
        while True:
            linecode = file.readline()
            if linecode == "":
                break
            event = self.parse_linecode_to_event(linecode)
            if event:
                event_list.append(event)
        return event_list

    def parse_linecode_to_event(self, linecode: str):
        j = json.loads(linecode)
        if j["opcode"] == "Barrier":
            return None
        event_id = j["event_id"]
        event_name = j["event_name"]
        event_dependency = j["dependency"]
        layer_name = j["basicblock_name"]
        if j["opcode"] == "CrossbarMult":
            tile_name = "tile_" + event_name.split("_xbar")[0]
            if tile_name not in self.hardware_dict:
                tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                self.hardware_dict[tile_name] = tile
            active_rows = j["active_rows"]
            active_cols = j["active_cols"]
            PE_idx = int(event_name.split("_PE")[1])
            xbar_mult_event = CrossbarMultEvent(event_name, event_id, event_dependency, EventStatus.wait, [1, active_rows], [active_rows, active_cols], self.hardware_dict[tile_name].PEs[PE_idx])
            return xbar_mult_event
        elif j["opcode"] == "Load":
            DRAM_name = "DRAM"
            if DRAM_name not in self.hardware_dict:
                dram = DRAM(DRAM_name, self.DRAM_config_path)
                self.hardware_dict["DRAM"] = dram
            size = j["size"]
            dst_name = j["dst_name"]
            dst_type = j["dst_type"]
            if dst_type == "TileInBuf":
                tile_name = "tile_" + dst_name.split("_" + dst_type)[0]
                if tile_name not in self.hardware_dict:
                    tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                    self.hardware_dict[tile_name] = tile
                load_event = LoadEvent(event_name,  event_id, event_dependency, EventStatus.wait, self.hardware_dict["DRAM"], self.hardware_dict[tile_name].tile_in_buf, size)
                return load_event
            elif dst_type == "VREG":
                if "on_FPGA" in j:
                    if self.fpga_name not in self.hardware_dict:
                        fpga = FPGA(self.fpga_name, self.FPGA_config_path)
                        self.hardware_dict[self.fpga_name] = fpga
                    dst = self.hardware_dict[self.fpga_name].FPGA_buf
                else:
                    tile_name = "tile_" + dst_name.split("_NVMReg")[0]
                    if tile_name not in self.hardware_dict:
                        tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                        self.hardware_dict[tile_name] = tile
                    dst = self.hardware_dict[tile_name].nonlinear_vec_module.nvm_buf
                load_event = LoadEvent(event_name,  event_id, event_dependency, EventStatus.wait, self.hardware_dict["DRAM"], dst, size)
            else:
                print(dst_type)
                assert(0)
        elif j["opcode"] == "CrossbarWrite":
            dst_name = j["dst_name"]
            tile_suffix = dst_name.split("_Xbar")[0]
            tile_name = "tile_" + tile_suffix
            if tile_name not in self.hardware_dict:
                tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                self.hardware_dict[tile_name] = tile
            PE_idx = int(dst_name.split("_Xbar_")[1])
            active_rows = j["active_rows"]
            active_cols = j["active_cols"]
            xbar_wr_event = CrossbarWriteEvent(event_name, event_id, event_dependency, EventStatus.wait, active_rows, active_cols, self.hardware_dict[tile_name].PEs[PE_idx])
            return xbar_wr_event
        elif j["opcode"] == "Move":
            size = j["size"]
            src_name = j["src_name"]
            src_type = j["src_type"]
            src = None
            if src_type == "TileOutBuf":
                tile_name = "tile_" + src_name.split("_" + src_type)[0]
                if tile_name not in self.hardware_dict:
                    tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                    self.hardware_dict[tile_name] = tile
                src = self.hardware_dict[tile_name].tile_out_buf
            elif src_type == "TileInBuf":
                tile_name = "tile_" + src_name.split("_" + src_type)[0]
                if tile_name not in self.hardware_dict:
                    tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                    self.hardware_dict[tile_name] = tile
                src = self.hardware_dict[tile_name].tile_in_buf
            elif src_type == "FPGABuf":
                if self.fpga_name not in self.hardware_dict:
                    fpga = FPGA(self.fpga_name, self.FPGA_config_path)
                    self.hardware_dict[self.fpga_name] = fpga
                src = self.hardware_dict[self.fpga_name].FPGA_buf
            elif src_type == "VREG":
                if "on_FPGA" in j:
                    if self.fpga_name not in self.hardware_dict:
                        fpga = FPGA(self.fpga_name, self.FPGA_config_path)
                        self.hardware_dict[self.fpga_name] = fpga
                    src = self.hardware_dict[self.fpga_name].NVM_reg
                else:
                    tile_name = "tile_" + src_name.split("_NVMReg")[0]
                    if tile_name not in self.hardware_dict:
                        tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                        self.hardware_dict[tile_name] = tile
                    src = self.hardware_dict[tile_name].nonlinear_vec_module.nvm_buf # TODO: check
            elif src_type == "Buf": # global buffer
                assert(0), "TODO: support"
            else:
                print(src_type)
                assert(0)
            dst_name = j["dst_name"]
            dst_type = j["dst_type"]
            dst = None
            if dst_type == "TileInBuf":
                tile_name = "tile_" + dst_name.split("_" + dst_type)[0]
                if tile_name not in self.hardware_dict:
                    tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                    self.hardware_dict[tile_name] = tile
                dst = self.hardware_dict[tile_name].tile_in_buf
            elif dst_type == "FPGABuf":
                if self.fpga_name not in self.hardware_dict:
                    fpga = FPGA(self.fpga_name, self.FPGA_config_path)
                    self.hardware_dict[self.fpga_name] = fpga
                dst = self.hardware_dict[self.fpga_name].FPGA_buf
            elif dst_type == "VREG":
                if "on_FPGA" in j:
                    if self.fpga_name not in self.hardware_dict:
                        fpga = FPGA(self.fpga_name, self.FPGA_config_path)
                        self.hardware_dict[self.fpga_name] = fpga
                    dst = self.hardware_dict[self.fpga_name].NVM_reg
                else:
                    tile_name = "tile_" + dst_name.split("_NVMReg")[0]
                    if tile_name not in self.hardware_dict:
                        tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                        self.hardware_dict[tile_name] = tile
                    dst = self.hardware_dict[tile_name].nonlinear_vec_module.nvm_buf # TODO: check
            elif dst_type == "Buf": # global buffer
                assert(0), "TODO: support"
            mv_event = MoveEvent(event_name, event_id, event_dependency, EventStatus.wait, src, dst, size)
            return mv_event
        elif j["opcode"] == "FPGABatMatmul":
            if self.fpga_name not in self.hardware_dict:
                fpga = FPGA(self.fpga_name, self.FPGA_config_path)
                self.hardware_dict[self.fpga_name] = fpga
            B = j["B"]
            M = j["M"]
            N = j["N"]
            P = j["P"]
            fpga_bmm_event = FPGABatMatmulEvent(event_name, event_id, event_dependency, EventStatus.wait, B, M, N, P, self.hardware_dict[self.fpga_name])
            return fpga_bmm_event
        elif j["opcode"] == "Vector":
            size = j["size"]
            vector_type = self.opcode_to_vector_dict[j["vector_opcode"]]
            if "on_FPGA" in j:
                if self.fpga_name not in self.hardware_dict:
                    fpga = FPGA(self.fpga_name, self.FPGA_config_path)
                    self.hardware_dict[self.fpga_name] = fpga
                vector_event = VectorEvent(event_name, event_id, event_dependency, EventStatus.wait, vector_type, size, size, self.hardware_dict[self.fpga_name])
                return vector_event
            else:
                src_name = j["src_1_name"]
                tile_name = "tile_" + src_name.split("_NVMReg")[0]
                if tile_name not in self.hardware_dict:
                    tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                    self.hardware_dict[tile_name] = tile
                vector_event = VectorEvent(event_name, event_id, event_dependency, EventStatus.wait, vector_type, size, size, self.hardware_dict[tile_name].nonlinear_vec_module)
                return vector_event
        elif j["opcode"] == "Reduce":
            size = j["size"]
            reduce_type = self.opcode_to_reduce_dict[j["reduce_opcode"]]
            if "on_FPGA" in j:
                if self.fpga_name not in self.hardware_dict:
                    fpga = FPGA(self.fpga_name, self.FPGA_config_path)
                    self.hardware_dict[self.fpga_name] = fpga
                reduce_event = ReduceEvent(event_name, event_id, event_dependency, EventStatus.wait, reduce_type, size, size, self.hardware_dict[self.fpga_name])
                return reduce_event
            else:
                src_name = j["src_1_name"]
                tile_name = "tile_" + src_name.split("_NVMReg")[0]
                if tile_name not in self.hardware_dict:
                    tile = Tile(tile_name, self.tile_config_path, self.tile_NVM_config_path)
                    self.hardware_dict[tile_name] = tile
                reduce_event = ReduceEvent(event_name, event_id, event_dependency, EventStatus.wait, reduce_type, size, size, self.hardware_dict[tile_name].nonlinear_vec_module)
                return reduce_event
        elif j["opcode"] == "PEMerge":
            # for now, PEMerge will only appear in CIMA, not FPGA
            src_name = j["src_name"]
            src_type = j["src_type"]
            dst_name = j["dst_name"]
            dst_type = j["dst_type"]
            len_1 = j["input_1_len"]
            len_2 = j["input_2_len"]
            if src_type == "TileOutBuf" and dst_type == "TileOutBuf":
                tile_name = tile_name = "tile_" + src_name.split("_TileOutBuf")[0]
                merge_event =  MergeEvent(event_name, event_id, event_dependency, EventStatus.wait, MergeEventType.MergeAdd, len_1, len_2, self.hardware_dict[tile_name].merge_unit)
                return merge_event
            else:
                assert(0)
        else:
            print(j["opcode"])
            assert(0)
            


