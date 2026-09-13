import Foundation
protocol Runner { func run() -> Int }
struct Xi: Runner { let id: Int; func run() -> Int { return id } }
func helper() -> Int { return Xi(id: 1).run() + Int(Date().timeIntervalSince1970) }
