"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Utensils, Wifi } from "lucide-react"
import Link from "next/link"

export default function Home() {
  const [phoneNumber, setPhoneNumber] = useState("")
  const [isScanning, setIsScanning] = useState(false)
  const [isValidPhoneNumber, setIsValidPhoneNumber] = useState(true)
  const [isDigitLimitExceeded, setIsDigitLimitExceeded] = useState(false)

  const validatePhoneNumber = (number: string) => {
    const phoneRegex = /^\d{3}-\d{3}-\d{4}$/
    return phoneRegex.test(number)
  }

  const handleScan = () => {
    setIsScanning(true)
    // Simulating a scan process
    setTimeout(() => setIsScanning(false), 3000)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validatePhoneNumber(phoneNumber)) {
      localStorage.setItem("phoneNumber", phoneNumber)
      window.location.href = "/link-device"
    } else {
      setIsValidPhoneNumber(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-200 to-orange-300 flex flex-col items-center justify-center p-4">
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
        className="text-5xl font-bold text-orange-600 mb-8 flex items-center"
      >
        <Utensils className="mr-4 h-12 w-12" />
        Raspitouille
      </motion.div>

      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-3xl shadow-xl p-8 w-full max-w-md"
      >
        <h2 className="text-2xl font-semibold text-gray-700 mb-6 text-center">Connect Your Device</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              type="tel"
              placeholder="Enter your phone number"
              value={phoneNumber}
              onChange={(e) => {
                const input = e.target.value.replace(/\D/g, "")
                if (input.length <= 10) {
                  let formattedInput = input
                  if (input.length > 3) {
                    formattedInput = `${input.slice(0, 3)}-${input.slice(3)}`
                  }
                  if (input.length > 6) {
                    formattedInput = `${formattedInput.slice(0, 7)}-${formattedInput.slice(7)}`
                  }
                  setPhoneNumber(formattedInput)
                  setIsValidPhoneNumber(true)
                  setIsDigitLimitExceeded(false)
                } else {
                  setIsDigitLimitExceeded(true)
                }
              }}
              className={`text-lg py-6 px-4 rounded-2xl border-2 ${
                isValidPhoneNumber && !isDigitLimitExceeded
                  ? "border-orange-300 focus:border-orange-500"
                  : "border-red-500 focus:border-red-600"
              } transition-colors`}
              required
            />
            {!isValidPhoneNumber && <p className="text-red-500 text-sm mt-1">Please enter a valid phone number.</p>}
            {isDigitLimitExceeded && <p className="text-red-500 text-sm mt-1">Phone number cannot exceed 10 digits.</p>}
          </div>

          <Button
            type="submit"
            className="w-full py-6 text-lg rounded-2xl bg-orange-500 hover:bg-orange-600 transition-colors"
          >
            Link Device
          </Button>

          <Button
            onClick={handleScan}
            disabled={isScanning}
            className="w-full py-6 text-lg rounded-2xl bg-blue-500 hover:bg-blue-600 transition-colors"
          >
            {isScanning ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
              >
                <Wifi className="mr-2 h-6 w-6" />
              </motion.div>
            ) : (
              <Wifi className="mr-2 h-6 w-6" />
            )}
            {isScanning ? "Scanning..." : "Scan for Devices"}
          </Button>
        </form>
      </motion.div>
      
    </div>
  )
}

