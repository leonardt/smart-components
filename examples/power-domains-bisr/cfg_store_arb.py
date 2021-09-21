import magma as m


from cfg_store import ConfigReq, ConfigData, CONFIG_CMD


class READ_STATE(m.Enum):
    IDLE = 0
    WAIT = 1


class ConfigStoreArbiter(m.Circuit):
    """
    Round robin, advance when a write occurs or after a read req/resp pair
    """
    io = m.IO(
        config_tx_in=m.Array[
            2,
            m.Tuple[
                m.Consumer(m.ReadyValid[ConfigReq]),
                m.Producer(m.ReadyValid[ConfigData])
            ]
        ],
        config_tx_out=m.Tuple[
            m.Producer(m.ReadyValid[ConfigReq]),
            m.Consumer(m.ReadyValid[ConfigData])
        ],
        boot=m.In(m.Bit)
    ) + m.ClockIO()

    # TODO: Add boot logic to hold ready/valid low
    booted = m.Register(m.Bit)()
    booted.I @= io.boot | booted.O

    state = m.Register(m.Bit, has_enable=True)()
    state.I @= state.O ^ 1

    # TODO: Mux of readyvalid array
    curr_req = m.Consumer(m.ReadyValid[ConfigReq])()
    curr_req.valid @= m.mux([
        io.config_tx_in[0][0].valid,
        io.config_tx_in[1][0].valid
    ], state.O)
    curr_req.data @= m.mux([
        io.config_tx_in[0][0].data,
        io.config_tx_in[1][0].data
    ], state.O)
    io.config_tx_in[0][0].ready @= m.mux([
        curr_req.ready,
        0
    ], state.O)
    io.config_tx_in[1][0].ready @= m.mux([
        0,
        curr_req.ready
    ], state.O)

    io.config_tx_in[0][1].valid @= m.mux([
        io.config_tx_out[1].valid,
        0
    ], state.O)
    io.config_tx_in[1][1].valid @= m.mux([
        0,
        io.config_tx_out[1].valid
    ], state.O)

    io.config_tx_in[0][1].data @= io.config_tx_out[1].data
    io.config_tx_in[1][1].data @= io.config_tx_out[1].data

    io.config_tx_out[1].ready @= m.mux([
        io.config_tx_in[0][1].ready,
        io.config_tx_in[1][1].ready
    ], state.O)

    read_req_tx = (io.config_tx_out[0].ready & curr_req.valid.value() &
                   (curr_req.data.value().cmd == CONFIG_CMD.READ))
    read_resp_tx = io.config_tx_out[1].ready.value() & io.config_tx_out[1].valid

    read_state = m.Register(READ_STATE)()
    read_state = m.mux([
        m.mux([READ_STATE.IDLE, READ_STATE.WAIT], read_req_tx),
        m.mux([READ_STATE.WAIT, READ_STATE.IDLE], read_resp_tx)
    ], read_state.O == READ_STATE.WAIT)

    state.CE @= (
        (io.config_tx_out[0].ready & io.config_tx_out[0].valid.value() &
         (io.config_tx_out[0].data.cmd.value() == CONFIG_CMD.WRITE)) |
        (read_resp_tx & (read_state.O == READ_STATE.WAIT))
    )


if __name__ == "__main__":
    m.compile("build/ConfigStoreArbiter", ConfigStoreArbiter)

