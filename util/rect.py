"""Utility functions for [pygame.Rect]s."""

import pygame


def create(center, size):
    """Create Rect given a [center] and [size]."""
    rect = pygame.Rect((0, 0), size)
    rect.center = center
    return rect
