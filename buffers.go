package nofs

type StatefulBuffer struct {
	Buffer []byte
	ReadPos int
}

func NewStatefulBuffer(size int) (*StatefulBuffer) {
	return &StatefulBuffer{make([]byte, size), 0}
}

func (sb *StatefulBuffer) Reset() {
	sb.ReadPos = 0
}

func (sb *StatefulBuffer) AtEnd() bool {
	return sb.ReadPos >= len(sb.Buffer)
}



type AppendBuffer struct {
	Buffer []byte
	WritePos int
}

func NewAppendBuffer(size int) (*AppendBuffer) {
	return &AppendBuffer{make([]byte, size), 0}
}

func (ab *AppendBuffer) Append(data byte) {
	wp := ab.WritePos
	ab.Buffer[wp] = data
	ab.WritePos++
}

func (ab *AppendBuffer) AppendSlice(data []byte) {
	wp := ab.WritePos
	copy(ab.Buffer[wp:wp+len(data)], data)
	ab.WritePos += len(data)
}

func (ab *AppendBuffer) Bytes() ([]byte) {
	return ab.Buffer[0:ab.WritePos]
}
