require 'json'
require_relative 'a'
class Eta
  def run
    JSON.generate({})
  end
end
def helper
  Eta.new.run
end
