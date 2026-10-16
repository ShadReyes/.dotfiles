import { theme } from "@oh-my-pi/pi-coding-agent";

export default function ricekit(pi) {
  pi.registerComposerShape({
    label: "Ricekit",
    description: "Input surface matching tool-result backgrounds",
    style: {
      id: "ricekit.input",
      filledSurface: false,
      sideBorders: false,
      verticalChrome: 0,
      statusAttachment: "none",
      bottomBar: "full",
      bottomBarGap: true,
      defaultPromptGutter: "❯ ",
      defaultPaddingX: () => 0,
      sideChromeWidth: () => 0,
      renderTop: () => undefined,
      renderRow: ({ gutter, text, pad }) => [
        theme.bgFill("toolPendingBg", gutter + text + pad),
      ],
      renderBottom: () => undefined,
    },
  });
}
