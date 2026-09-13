import kotlin.math.abs
import java.io.File
class Nu(val id: Int) {
    fun run(): Int = abs(id)
}
fun helper(): Int = Nu(1).run() + File(".").name.length
