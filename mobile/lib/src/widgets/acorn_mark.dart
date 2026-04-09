import 'package:flutter/material.dart';

import '../brand.dart';

class AcornMark extends StatelessWidget {
  const AcornMark({
    super.key,
    this.size = 52,
  });

  final double size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: const _AcornMarkPainter(),
      ),
    );
  }
}

class _AcornMarkPainter extends CustomPainter {
  const _AcornMarkPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final width = size.width;
    final height = size.height;

    final stem = Path()
      ..moveTo(width * 0.57, height * 0.1)
      ..cubicTo(
        width * 0.73,
        height * 0.1,
        width * 0.81,
        height * 0.02,
        width * 0.82,
        height * 0,
      )
      ..cubicTo(
        width * 0.61,
        height * 0,
        width * 0.43,
        height * 0.11,
        width * 0.44,
        height * 0.3,
      )
      ..cubicTo(
        width * 0.49,
        height * 0.2,
        width * 0.53,
        height * 0.1,
        width * 0.57,
        height * 0.1,
      )
      ..close();

    final cap = Path()
      ..moveTo(width * 0.18, height * 0.42)
      ..cubicTo(
        width * 0.24,
        height * 0.29,
        width * 0.37,
        height * 0.2,
        width * 0.5,
        height * 0.2,
      )
      ..cubicTo(
        width * 0.63,
        height * 0.2,
        width * 0.76,
        height * 0.29,
        width * 0.82,
        height * 0.42,
      )
      ..cubicTo(
        width * 0.84,
        height * 0.46,
        width * 0.81,
        height * 0.5,
        width * 0.76,
        height * 0.5,
      )
      ..lineTo(width * 0.24, height * 0.5)
      ..cubicTo(
        width * 0.19,
        height * 0.5,
        width * 0.16,
        height * 0.46,
        width * 0.18,
        height * 0.42,
      )
      ..close();

    final nut = Path()
      ..moveTo(width * 0.5, height * 0.34)
      ..cubicTo(
        width * 0.69,
        height * 0.34,
        width * 0.81,
        height * 0.47,
        width * 0.79,
        height * 0.66,
      )
      ..cubicTo(
        width * 0.77,
        height * 0.81,
        width * 0.66,
        height * 0.93,
        width * 0.5,
        height * 0.99,
      )
      ..cubicTo(
        width * 0.34,
        height * 0.93,
        width * 0.23,
        height * 0.81,
        width * 0.21,
        height * 0.66,
      )
      ..cubicTo(
        width * 0.19,
        height * 0.47,
        width * 0.31,
        height * 0.34,
        width * 0.5,
        height * 0.34,
      )
      ..close();

    canvas.drawPath(stem, Paint()..color = BrandColors.harvest);
    canvas.drawPath(nut, Paint()..color = BrandColors.copper);
    canvas.drawPath(cap, Paint()..color = BrandColors.olive);
  }

  @override
  bool shouldRepaint(covariant _AcornMarkPainter oldDelegate) {
    return false;
  }
}
