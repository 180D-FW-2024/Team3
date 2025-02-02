"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { QrCode as QrCodeIcon, ArrowLeft } from "lucide-react"
import QRCode from "react-qr-code";
import Link from "next/link";

import axios from "axios";

const BACKEND_URL = 'http://localhost:5001'// 'https://suitable-kangaroo-immensely.ngrok-free.app'

const BOTNAME = "RaspitouilleBot"

export default function LinkDevice() {
  const [qrValue, setQrValue] = useState<string>("")
  const [telegramQR, setTelegramQR] = useState<string>("")

  interface ConnectTelegramResponse {
    join_code: string;
  }

  useEffect(() => {
    // In a real application, you would generate this value server-side
    // and possibly include a timestamp or other security measures
    // const deviceId = Math.random().toString(36).substring(7)
    const phoneNumber = localStorage.getItem("phoneNumber") as string || ""
    setQrValue(JSON.stringify({ phoneNumber }))

    console.log("Getting code for phone number " + phoneNumber + " at " + `${BACKEND_URL}/connect-telegram`)

    axios.get<ConnectTelegramResponse>(`${BACKEND_URL}/connect-telegram`, { params: { phone_number: phoneNumber } })
      .then((response) => {
        console.log("Response data: " + JSON.stringify(response.data))
        setTelegramQR(`https://telegram.me/${BOTNAME}?start=${response.data.join_code}`)
        console.log('Got code ' + response.data.join_code)
      })
      .catch((error) => {
        console.error(error)
      })
  }, [location.pathname])

  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-200 to-orange-300 flex flex-col items-center justify-center p-4">
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
        className="bg-white rounded-3xl shadow-xl p-8 w-full max-w-md"
      >
        <h2 className="text-2xl font-semibold text-gray-700 mb-6 text-center flex items-center justify-center">
          Link Your Device
        </h2>
  
        <div className="flex flex-col items-center space-y-6">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <QRCode value={qrValue} size={200} />
          </motion.div>

          <p className="text-center text-gray-600">
            Scan this QR code with your cooking device to link it with your account.
          </p>
        </div>

        <h2 className="text-2xl font-semibold text-gray-700 mb-6 text-center flex items-center justify-center">
          <Link href={telegramQR}>
          <Button variant="ghost" size="xlg">
            Link Your Telegram
          </Button>

          </Link>
        </h2>
        <div className="flex flex-col items-center space-y-6">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <QRCode value={telegramQR} size={200} />
          </motion.div>

          <p className="text-center text-gray-600">
            Scan this QR code with your phone to link telegram with your account for notifications.
          </p>

          <Link href="/">
            <Button variant="outline" className="mt-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}

