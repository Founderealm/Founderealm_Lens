package main
import "fmt"
import "os"
type Epsilon struct{ id int }
func (e Epsilon) Run() int { return e.id }
func helper() { fmt.Println(os.Getpid(), Epsilon{id: 1}.Run()) }
