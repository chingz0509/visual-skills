import Foundation
import Vision
import CoreImage
import ImageIO
import UniformTypeIdentifiers

// Segmentation supplies an alpha mask only; original RGB is composed in Python.
let args = CommandLine.arguments
func die(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8)); exit(1)
}
guard args.count >= 4 else { die("Usage: vision mask|ocr input output") }
let mode = args[1], input = URL(fileURLWithPath: args[2]), output = URL(fileURLWithPath: args[3])
let handler = VNImageRequestHandler(url: input, options: [:])
do {
    if mode == "mask" {
        if #available(macOS 14.0, *) {
            let request = VNGenerateForegroundInstanceMaskRequest()
            try handler.perform([request])
            guard let result = request.results?.first, !result.allInstances.isEmpty else { die("No foreground instances detected") }
            let buffer = try result.generateScaledMaskForImage(forInstances: result.allInstances, from: handler)
            let image = CIImage(cvPixelBuffer: buffer)
            let context = CIContext()
            guard let cg = context.createCGImage(image, from: image.extent),
                  let dest = CGImageDestinationCreateWithURL(output as CFURL, UTType.png.identifier as CFString, 1, nil) else { die("Cannot write mask") }
            CGImageDestinationAddImage(dest, cg, nil)
            guard CGImageDestinationFinalize(dest) else { die("Mask write failed") }
            print("mask instances=\(result.allInstances.count)")
        } else { die("Foreground masking requires macOS 14+") }
    } else if mode == "ocr" {
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["zh-Hans", "en-US"]
        request.usesLanguageCorrection = false
        try handler.perform([request])
        let lines = (request.results ?? []).compactMap { observation -> [String: Any]? in
            guard let candidate = observation.topCandidates(1).first else { return nil }
            return ["text": candidate.string, "confidence": candidate.confidence,
                    "box": [observation.boundingBox.origin.x, observation.boundingBox.origin.y, observation.boundingBox.width, observation.boundingBox.height]]
        }
        try JSONSerialization.data(withJSONObject: lines, options: [.prettyPrinted, .sortedKeys]).write(to: output)
    } else { die("Unknown mode") }
} catch { die(String(describing: error)) }
