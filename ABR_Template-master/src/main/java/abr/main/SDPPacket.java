package abr.main;

import java.nio.ByteBuffer;

//============================================================================
// SDPPacket
//============================================================================
// SpiNNaker data packet
public class SDPPacket
{
    //============================================================================
    // Constants
    //============================================================================
    private static final int FLAG_REPLY = 0x87;
    private static final int FLAG_NO_REPLY = 0x07;

    public SDPPacket(byte[] data)
    {
        // Wrap header bytes from incoming data into byte buffer
        // **NOTE** ignore first two bytes
        ByteBuffer headerByteBuffer = ByteBuffer.wrap(data, 2, 8);

        // Read header words
        int flags = (int)headerByteBuffer.get();
        m_Tag = (int)headerByteBuffer.get();
        int destCPUPort = (int)headerByteBuffer.get();
        int srcCPUPort = (int)headerByteBuffer.get();
        m_DestY = (int)headerByteBuffer.get();
        m_DestX = (int)headerByteBuffer.get();
        m_SrcY = (int)headerByteBuffer.get();
        m_SrcX = (int)headerByteBuffer.get();

        // Unpack packed header words
        m_DestCPU = destCPUPort & 0x1F;
        m_DestPort = destCPUPort >> 5;
        m_SrcCPU = srcCPUPort & 0x1F;
        m_SrcPort = srcCPUPort >> 5;

        m_ReplyExpected = (flags == FLAG_REPLY);

        // Wrap payload in second byte buffer
        m_Data = ByteBuffer.wrap(data, 10, data.length - 10);
    }

    //============================================================================
    // Getters
    //============================================================================
    public int get_Tag() {
        return m_Tag;
    }

    public int get_DestCPU() {
        return m_DestCPU;
    }

    public int get_DestPort() {
        return m_DestPort;
    }

    public int get_DestX() {
        return m_DestX;
    }

    public int get_DestY() {
        return m_DestY;
    }

    public int get_SrcCPU() {
        return m_SrcCPU;
    }

    public int get_SrcPort() {
        return m_SrcPort;
    }

    public int get_SrcX() {
        return m_SrcX;
    }

    public int get_SrcY() {
        return m_SrcY;
    }

    public boolean is_ReplyExpected() {
        return m_ReplyExpected;
    }

    public ByteBuffer get_Data() {
        return m_Data;
    }

    //============================================================================
    // Private members
    //============================================================================
    private int m_Tag;
    private int m_DestCPU;
    private int m_DestPort;
    private int m_DestX;
    private int m_DestY;
    private int m_SrcCPU;
    private int m_SrcPort;
    private int m_SrcX;
    private int m_SrcY;

    private boolean m_ReplyExpected;

    private ByteBuffer m_Data;
}